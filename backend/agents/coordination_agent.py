class CoordinationAgent:
    """
    Person 4: Coordination & Allocation Agent
    Core AI: Multi-Objective Constrained Optimization & Conflict Resolution
    """
    def __init__(self):
        self.active_assignments = {}

    def allocate(self, patient_reqs: dict, routes: list, hospitals_status: dict) -> dict:
        if not routes:
            return {
                "status": "FAILED",
                "reason": "No feasible hospitals found matching clinical requirements, specialist availability, and bed capacity.",
                "assigned_hospital": None,
                "assigned_hospital_name": None,
                "eta": 0,
                "score": 0,
                "alternatives": []
            }
            
        time_sensitivity = patient_reqs.get("time_sensitivity", "NORMAL")
        w_eta = 1.3 if time_sensitivity == "CRITICAL" else 1.0
        w_er = 10.0
        w_dist = 0.3
        
        scored_candidates = []
        for route in routes:
            h_id = route["hospital_id"]
            h_data = hospitals_status.get(h_id, {})
            
            eta = route["actual_eta_min"]
            er_occupancy = float(h_data.get("er_occupancy", 0.5))
            distance = route["distance_km"]
            
            # Optimization score: Lower score is better
            score = round((eta * w_eta) + (er_occupancy * w_er) + (distance * w_dist), 2)
            
            scored_candidates.append({
                "hospital_id": h_id,
                "name": route["name"],
                "score": score,
                "eta": eta,
                "distance_km": distance,
                "er_occupancy": round(er_occupancy * 100, 1),
                "route_status": route["route_status"]
            })
            
        scored_candidates.sort(key=lambda x: x["score"])
        best = scored_candidates[0]
        
        decision = {
            "status": "SUCCESS",
            "assigned_hospital": best["hospital_id"],
            "assigned_hospital_name": best["name"],
            "eta": best["eta"],
            "distance_km": best["distance_km"],
            "score": best["score"],
            "reason": f"Allocated to {best['name']} based on optimal multi-agent score ({best['score']}). ETA: {best['eta']} min ({best['distance_km']} km), ER occupancy: {best['er_occupancy']}%.",
            "alternatives": scored_candidates[1:]
        }
        
        self.active_assignments[patient_reqs.get("patient_id")] = decision
        return decision

    def handle_event_and_replan(self, event: dict, current_assignment: dict, all_agents_re_eval: dict) -> dict:
        return self.allocate(
            all_agents_re_eval["reqs"], 
            all_agents_re_eval["routes"], 
            all_agents_re_eval["hospitals_status"]
        )
