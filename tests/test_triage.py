import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from agents.triage_agent import TriageAgent

class TestTriageAgent(unittest.TestCase):
    def setUp(self):
        self.agent = TriageAgent()

    def test_stemi_cardiac_arrest(self):
        patient = {
            "id": "P001",
            "emergency_type": "CARDIAC_ARREST",
            "severity": "CRITICAL",
            "spo2": 86,
            "heart_rate": 145,
            "consciousness": "ALTERED"
        }
        res = self.agent.evaluate_patient(patient)
        self.assertEqual(res["priority"], "P1")
        self.assertEqual(res["time_sensitivity"], "CRITICAL")
        self.assertEqual(res["specialist"], "CARDIOLOGY")
        self.assertTrue(res["icu_required"])

    def test_stroke_golden_hour(self):
        patient = {
            "id": "P002",
            "emergency_type": "STROKE",
            "severity": "CRITICAL",
            "spo2": 95,
            "heart_rate": 88,
            "consciousness": "ALTERED"
        }
        res = self.agent.evaluate_patient(patient)
        self.assertEqual(res["priority"], "P1")
        self.assertEqual(res["specialist"], "NEUROLOGY")
        self.assertTrue(res["ct_scan_required"])

    def test_polytrauma_shock(self):
        patient = {
            "id": "P003",
            "emergency_type": "SEVERE_TRAUMA",
            "severity": "CRITICAL",
            "spo2": 82,
            "heart_rate": 130,
            "consciousness": "UNRESPONSIVE"
        }
        res = self.agent.evaluate_patient(patient)
        self.assertEqual(res["priority"], "P1")
        self.assertTrue(res["trauma_required"])
        self.assertTrue(res["ct_scan_required"])
        self.assertTrue(res["icu_required"])

    def test_severe_burn_unit(self):
        patient = {
            "id": "P004",
            "emergency_type": "BURN",
            "severity": "CRITICAL",
            "spo2": 91,
            "heart_rate": 115,
            "consciousness": "ALERT"
        }
        res = self.agent.evaluate_patient(patient)
        self.assertEqual(res["specialist"], "BURN")

    def test_urology_emergency(self):
        patient = {
            "id": "P005",
            "emergency_type": "UROLOGY_EMERGENCY",
            "severity": "HIGH",
            "spo2": 98,
            "heart_rate": 84,
            "consciousness": "ALERT"
        }
        res = self.agent.evaluate_patient(patient)
        self.assertEqual(res["specialist"], "UROLOGY")

    def test_ocular_emergency(self):
        patient = {
            "id": "P006",
            "emergency_type": "EYE_TRAUMA",
            "severity": "HIGH",
            "spo2": 99,
            "heart_rate": 78,
            "consciousness": "ALERT"
        }
        res = self.agent.evaluate_patient(patient)
        self.assertEqual(res["specialist"], "OPHTHALMOLOGY")

if __name__ == "__main__":
    unittest.main()
