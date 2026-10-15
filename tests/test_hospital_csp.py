import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from agents.hospital_agent import HospitalAgent

class TestHospitalCSP(unittest.TestCase):
    def setUp(self):
        self.mock_hospitals = {
            "H_VALID": {
                "hospital_id": "H_VALID",
                "name": "Super Specialty Trauma",
                "icu_available": 3,
                "icu_total": 10,
                "er_occupancy": 0.40,
                "trauma_capability": True,
                "specialists_available": ["CARDIOLOGY", "NEUROLOGY", "TRAUMA"],
                "ct_scan": True
            },
            "H_NO_ICU": {
                "hospital_id": "H_NO_ICU",
                "name": "Full ICU Hospital",
                "icu_available": 0,
                "icu_total": 10,
                "er_occupancy": 0.50,
                "trauma_capability": True,
                "specialists_available": ["CARDIOLOGY", "TRAUMA"],
                "ct_scan": True
            },
            "H_NO_SPECIALIST": {
                "hospital_id": "H_NO_SPECIALIST",
                "name": "General Clinic",
                "icu_available": 5,
                "icu_total": 10,
                "er_occupancy": 0.30,
                "trauma_capability": False,
                "specialists_available": ["GENERAL_SURGERY"],
                "ct_scan": True
            },
            "H_ER_FULL": {
                "hospital_id": "H_ER_FULL",
                "name": "Saturated ER Hospital",
                "icu_available": 2,
                "icu_total": 10,
                "er_occupancy": 0.96, # 96% full
                "trauma_capability": True,
                "specialists_available": ["CARDIOLOGY", "TRAUMA"],
                "ct_scan": True
            }
        }
        self.agent = HospitalAgent(self.mock_hospitals)

    def test_csp_filtering_icu_zero(self):
        reqs = {
            "icu_required": True,
            "trauma_required": False,
            "specialist": "CARDIOLOGY",
            "ct_scan_required": False
        }
        res = self.agent.find_feasible_hospitals(reqs)
        feasible_ids = [h["hospital_id"] for h in res["feasible_hospitals"]]
        self.assertIn("H_VALID", feasible_ids)
        self.assertNotIn("H_NO_ICU", feasible_ids)

    def test_csp_filtering_specialist(self):
        reqs = {
            "icu_required": False,
            "trauma_required": False,
            "specialist": "NEUROLOGY",
            "ct_scan_required": False
        }
        res = self.agent.find_feasible_hospitals(reqs)
        feasible_ids = [h["hospital_id"] for h in res["feasible_hospitals"]]
        self.assertIn("H_VALID", feasible_ids)
        self.assertNotIn("H_NO_SPECIALIST", feasible_ids)

    def test_csp_filtering_er_saturation(self):
        reqs = {
            "icu_required": True,
            "trauma_required": False,
            "specialist": "CARDIOLOGY",
            "ct_scan_required": False
        }
        res = self.agent.find_feasible_hospitals(reqs)
        feasible_ids = [h["hospital_id"] for h in res["feasible_hospitals"]]
        self.assertNotIn("H_ER_FULL", feasible_ids)

if __name__ == "__main__":
    unittest.main()
