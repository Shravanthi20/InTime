import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from agents.coordination_agent import CoordinationAgent

class TestCoordinationAndReplanning(unittest.TestCase):
    def setUp(self):
        self.agent = CoordinationAgent()

    def test_multi_objective_penalizes_er_occupancy(self):
        """
        Verify that a closer hospital with an overcrowded ER (90%) is rejected
        in favor of a hospital slightly further with an empty ER (10%).
        """
        routes = [
            {
                "hospital_id": "H_A_CLOSER_CROWDED",
                "name": "Hospital A",
                "actual_eta_min": 5.0,
                "distance_km": 3.0,
                "route_status": "OPTIMAL"
            },
            {
                "hospital_id": "H_B_FURTHER_EMPTY",
                "name": "Hospital B",
                "actual_eta_min": 7.0,
                "distance_km": 4.5,
                "route_status": "OPTIMAL"
            }
        ]
        
        hospitals_status = {
            "H_A_CLOSER_CROWDED": {"er_occupancy": 0.90}, # 90% full
            "H_B_FURTHER_EMPTY": {"er_occupancy": 0.10}   # 10% full
        }
        
        patient_reqs = {"time_sensitivity": "CRITICAL", "patient_id": "P_TEST"}
        decision = self.agent.allocate(patient_reqs, routes, hospitals_status)
        
        self.assertEqual(decision["status"], "SUCCESS")
        # Hospital B should win due to lower total loss score
        self.assertEqual(decision["assigned_hospital"], "H_B_FURTHER_EMPTY")
        self.assertLess(decision["score"], 15.0)

    def test_dynamic_replanning_diversion(self):
        """Verify dynamic contingency failover when disruption occurs."""
        current_assignment = {
            "assigned_hospital": "H_ORIGINAL",
            "assigned_hospital_name": "Hospital Original",
            "score": 8.5
        }
        
        # Original hospital is now saturated or blocked, alternate is available
        all_agents_re_eval = {
            "reqs": {"time_sensitivity": "CRITICAL", "patient_id": "P_TEST"},
            "routes": [
                {
                    "hospital_id": "H_ALTERNATE",
                    "name": "Hospital Alternate",
                    "actual_eta_min": 6.0,
                    "distance_km": 4.0,
                    "route_status": "OPTIMAL"
                }
            ],
            "hospitals_status": {
                "H_ALTERNATE": {"er_occupancy": 0.20}
            }
        }
        
        event = {
            "type": "CAPACITY_CHANGE",
            "target_id": "H_ORIGINAL",
            "desc": "Hospital Original ICU reached 100% saturation"
        }
        
        replan = self.agent.handle_event_and_replan(event, current_assignment, all_agents_re_eval)
        self.assertEqual(replan["status"], "SUCCESS")
        self.assertEqual(replan["assigned_hospital"], "H_ALTERNATE")
        self.assertTrue(replan["replanned"])
        self.assertIn("DYNAMIC REPLAN", replan["replan_reason"])

if __name__ == "__main__":
    unittest.main()
