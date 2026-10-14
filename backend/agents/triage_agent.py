class TriageAgent:
    """
    Person 1: Triage & Patient Requirement Agent
    Core AI: Clinical Rule-Based Inference & Requirement Extraction Engine
    """
    def __init__(self):
        pass

    def evaluate_patient(self, patient_data: dict) -> dict:
        emergency_type = str(patient_data.get("emergency_type", "GENERAL_EMERGENCY")).upper()
        severity = str(patient_data.get("severity", "MODERATE")).upper()
        spo2 = int(patient_data.get("spo2", 98))
        heart_rate = int(patient_data.get("heart_rate", 80))
        consciousness = str(patient_data.get("consciousness", "ALERT")).upper()

        # Baseline requirements
        requirements = {
            "patient_id": patient_data.get("id", "P-UNKNOWN"),
            "emergency_type": emergency_type,
            "severity": severity,
            "priority": "P3",
            "time_sensitivity": "NORMAL",
            "icu_required": False,
            "trauma_required": False,
            "ct_scan_required": False,
            "oxygen_required": False,
            "specialist": None,
            "explanation": ""
        }
        
        reasons = []

        # 1. Base Emergency Type Clinical Protocol
        if "CARDIAC" in emergency_type:
            requirements["specialist"] = "CARDIOLOGY"
            requirements["icu_required"] = True
            requirements["oxygen_required"] = True
            requirements["priority"] = "P1"
            requirements["time_sensitivity"] = "CRITICAL"
            reasons.append("Cardiac emergency: Cardiology specialist, immediate ICU standby, and continuous telemetry required.")

        elif "STROKE" in emergency_type:
            requirements["specialist"] = "NEUROLOGY"
            requirements["ct_scan_required"] = True
            requirements["time_sensitivity"] = "CRITICAL"
            requirements["priority"] = "P1"
            if severity in ["CRITICAL", "HIGH"]:
                requirements["icu_required"] = True
            reasons.append("Acute Stroke protocol: Golden-hour Neurology consultation, 24/7 emergency CT scan, and Neuro-ICU pathway.")

        elif "EYE" in emergency_type or "OPHTHALM" in emergency_type:
            requirements["specialist"] = "OPHTHALMOLOGY"
            requirements["priority"] = "P2" if severity in ["CRITICAL", "HIGH"] else "P3"
            requirements["time_sensitivity"] = "HIGH"
            reasons.append("Ocular emergency: Specialized Ophthalmology center, emergency microsurgery, and vision preservation.")

        elif "TRAUMA" in emergency_type:
            requirements["specialist"] = "TRAUMA"
            requirements["trauma_required"] = True
            requirements["ct_scan_required"] = True
            if severity in ["CRITICAL", "HIGH"]:
                requirements["icu_required"] = True
                requirements["priority"] = "P1"
                requirements["time_sensitivity"] = "CRITICAL"
            else:
                requirements["priority"] = "P2"
                requirements["time_sensitivity"] = "HIGH"
            reasons.append("Severe Trauma protocol: Certified Level-1/2 Trauma Center, emergency surgical resuscitation, and full trauma team.")

        elif "BURN" in emergency_type:
            requirements["specialist"] = "BURN"
            requirements["icu_required"] = True
            if severity in ["CRITICAL", "HIGH"]:
                requirements["priority"] = "P1"
                requirements["time_sensitivity"] = "CRITICAL"
            else:
                requirements["priority"] = "P2"
                requirements["time_sensitivity"] = "HIGH"
            reasons.append("Burn injury protocol: Specialized Burn / Plastic Surgery unit, sterile ICU isolation, and intensive fluid management.")

        elif "FRACTURE" in emergency_type:
            requirements["specialist"] = "ORTHOPEDICS"
            if severity == "CRITICAL":
                requirements["trauma_required"] = True
                requirements["priority"] = "P2"
                requirements["time_sensitivity"] = "HIGH"
                reasons.append("Severe/compound orthopedic injury: Orthopedic surgical team, emergency stabilization, and trauma support.")
            else:
                requirements["priority"] = "P3"
                requirements["time_sensitivity"] = "MODERATE"
                reasons.append("Orthopedic fracture: Orthopedics specialist required for closed/open reduction and immobilization.")

        elif "RESPIRATORY" in emergency_type:
            requirements["specialist"] = "PULMONOLOGY"
            requirements["icu_required"] = True
            requirements["oxygen_required"] = True
            requirements["priority"] = "P1" if severity in ["CRITICAL", "HIGH"] else "P2"
            requirements["time_sensitivity"] = "CRITICAL" if severity == "CRITICAL" else "HIGH"
            reasons.append("Acute respiratory failure: Pulmonology specialist, mechanical ventilation capability, and ICU monitoring.")

        elif "UROLOGY" in emergency_type or "KIDNEY" in emergency_type:
            requirements["specialist"] = "UROLOGY"
            requirements["priority"] = "P2" if severity in ["CRITICAL", "HIGH"] else "P3"
            requirements["time_sensitivity"] = "HIGH" if severity == "CRITICAL" else "MODERATE"
            reasons.append("Acute Urological/Nephrology emergency: Urology specialist, renal diagnostics, and surgical intervention.")


        else:
            requirements["specialist"] = "GENERAL_SURGERY"
            requirements["priority"] = "P3"
            requirements["time_sensitivity"] = "NORMAL"
            reasons.append("General emergency protocol: General medical / surgical evaluation.")

        # 2. Physiological Vitals & Acuity Escalation
        if spo2 < 90:
            requirements["icu_required"] = True
            requirements["oxygen_required"] = True
            requirements["priority"] = "P1"
            reasons.append(f"Severe hypoxia detected (SpO2 {spo2}% < 90%): Immediate oxygen and ICU admission mandated.")
        elif spo2 < 94:
            requirements["oxygen_required"] = True
            reasons.append(f"Borderline hypoxia (SpO2 {spo2}%): Supplementary oxygen support recommended.")

        if heart_rate > 120:
            reasons.append(f"Tachycardia alert (Heart rate {heart_rate} bpm > 120 bpm).")
        elif heart_rate < 50:
            reasons.append(f"Bradycardia alert (Heart rate {heart_rate} bpm < 50 bpm).")

        if consciousness in ["UNRESPONSIVE", "ALTERED"]:
            requirements["priority"] = "P1"
            requirements["icu_required"] = True
            reasons.append(f"Altered mental status / GCS depression ({consciousness}): Critical priority escalation, ICU standby.")

        if severity == "CRITICAL":
            requirements["priority"] = "P1"
            requirements["time_sensitivity"] = "CRITICAL"

        requirements["explanation"] = " | ".join(reasons)
        return requirements
