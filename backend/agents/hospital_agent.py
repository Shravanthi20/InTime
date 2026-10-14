class HospitalAgent:
    """
    Person 2: Hospital Capability & Clinical Constraint Agent
    Core AI: Constraint Satisfaction & Medical Capability Filtering
    """
    def __init__(self, hospitals_db: dict):
        self.hospitals_db = hospitals_db

    def find_feasible_hospitals(self, requirements: dict) -> dict:
        results = []
        
        for h_id, h_data in self.hospitals_db.items():
            feasible = True
            rejection_reasons = []
            
            # Constraint 1: ICU Availability
            if requirements.get("icu_required") and h_data.get("icu_available", 0) <= 0:
                feasible = False
                rejection_reasons.append(f"ICU unavailable (0/{h_data.get('icu_total', 0)} beds free)")
                
            # Constraint 2: Certified Trauma Center
            if requirements.get("trauma_required") and not h_data.get("trauma_capability"):
                feasible = False
                rejection_reasons.append("Lacks certified 24/7 Trauma Emergency Center")
                
            # Constraint 3: Medical Specialist Match
            req_spec = requirements.get("specialist")
            if req_spec:
                avail_specs = h_data.get("specialists_available", [])
                
                # Special handling for BURN: accepts either BURN or PLASTIC_SURGERY
                if req_spec == "BURN":
                    if not any(s in avail_specs for s in ["BURN", "PLASTIC_SURGERY"]):
                        feasible = False
                        rejection_reasons.append("No specialized Burn / Plastic Surgery unit")
                elif req_spec not in avail_specs:
                    feasible = False
                    rejection_reasons.append(f"Specialist '{req_spec}' not available")

            # Constraint 4: Emergency CT Scan Facility
            if requirements.get("ct_scan_required") and not h_data.get("ct_scan", False):
                feasible = False
                rejection_reasons.append("24/7 Emergency CT Scan facility unavailable")

            # Constraint 5: ER Overload
            if h_data.get("er_occupancy", 0) > 0.95:
                feasible = False
                rejection_reasons.append(f"ER critically saturated ({int(h_data.get('er_occupancy', 0) * 100)}% occupancy)")
                
            if feasible:
                rejection_reasons.append("All clinical, specialist, equipment, and bed constraints satisfied.")
                
            results.append({
                "hospital_id": h_id,
                "name": h_data.get("name"),
                "feasible": feasible,
                "rejection_reasons": rejection_reasons,
                "current_icu": h_data.get("icu_available"),
                "er_occupancy": h_data.get("er_occupancy"),
                "specialists": h_data.get("specialists_available", []),
                "latitude": h_data.get("latitude"),
                "longitude": h_data.get("longitude")
            })
            
        return {
            "feasible_hospitals": [r for r in results if r["feasible"]],
            "rejected_hospitals": [r for r in results if not r["feasible"]],
            "all_evaluations": results
        }
