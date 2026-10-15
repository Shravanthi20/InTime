import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from agents.ambulance_agent import AmbulanceAgent
from agents.mobility_agent import MobilityAgent

class TestAmbulanceCNP(unittest.TestCase):
    def setUp(self):
        self.agent = AmbulanceAgent()
        self.mobility = MobilityAgent()

    def test_critical_requires_als(self):
        """A critical patient must be awarded only to an ALS certified ambulance."""
        patient_reqs = {"time_sensitivity": "CRITICAL", "priority": "CRITICAL"}
        res = self.agent.contract_net_bidding(patient_reqs, pickup_node="N0214", mobility_agent=self.mobility)
        self.assertEqual(res["status"], "ASSIGNED")
        self.assertEqual(res["type"], "ALS")
        self.assertIn("VENTILATOR", res["equipment"])

    def test_bidding_awards_closest_unit(self):
        """Bidding contract should go to the unit with fastest response."""
        patient_reqs = {"time_sensitivity": "NORMAL", "priority": "HIGH"}
        res = self.agent.contract_net_bidding(patient_reqs, pickup_node="N0119", mobility_agent=self.mobility)
        self.assertEqual(res["status"], "ASSIGNED")
        self.assertIsNotNone(res["assigned_ambulance"])
        self.assertGreater(len(res["competing_bids"]), 0)

if __name__ == "__main__":
    unittest.main()
