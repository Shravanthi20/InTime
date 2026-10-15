class CoordinationAgent:
    """
    Agent 4: Coordination & Allocation Agent
    Core AI: Multi-Objective Constrained Optimization (MOCO), Loss Minimization,
    and Dynamic Contingency Failover Replanning.
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
        # Critical emergencies weight ETA 30% higher to prioritize definitive care window
        w_eta = 1.3 if time_sensitivity == "CRITICAL" else 1.0
        w_er = 10.0 # Heavy penalty for crowded emergency rooms (prevents hallway delays)
        w_dist = 0.3 # Tie-breaker distance penalty
        
        scored_candidates = []
        for route in routes:
            h_id = route["hospital_id"]
            h_data = hospitals_status.get(h_id, {})
            
            eta = route["actual_eta_min"]
            er_occupancy = float(h_data.get("er_occupancy", 0.5))
            distance = route["distance_km"]
            
            # Loss Function: L = (w_eta * ETA) + (w_er * ER_Occupancy) + (w_dist * Distance)
            # Lower score represents Pareto-superior allocation
            score = round((eta * w_eta) + (er_occupancy * w_er) + (distance * w_dist), 2)
            
            scored_candidates.append({
                "hospital_id": h_id,
                "name": route["name"],
                "score": score,
                "eta": eta,
                "distance_km": distance,
                "er_occupancy": round(er_occupancy * 100, 1),
                "route_status": route.get("route_status", "OPTIMAL"),
                "search_metrics": route.get("search_metrics", {})
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
            "loss_weights": {"w_eta": w_eta, "w_er": w_er, "w_dist": w_dist},
            "alternatives": scored_candidates[1:]
        }
        
        self.active_assignments[patient_reqs.get("patient_id", "P1001")] = decision
        return decision

    def handle_event_and_replan(self, event: dict, current_assignment: dict, all_agents_re_eval: dict) -> dict:
        """
        Dynamically reacts to real-time disruptions (ICU saturation or road blocks)
        and executes fast contingency failover without restarting the system.
        """
        previous_hospital = current_assignment.get("assigned_hospital_name") or current_assignment.get("assigned_hospital", "Unknown")
        previous_score = current_assignment.get("score", 0)
        
        new_decision = self.allocate(
            all_agents_re_eval["reqs"], 
            all_agents_re_eval["routes"], 
            all_agents_re_eval["hospitals_status"]
        )
        
        if new_decision["status"] == "SUCCESS":
            new_hospital = new_decision["assigned_hospital_name"]
            evt_desc = event.get("desc", event.get("type", "Disruption"))
            
            new_decision["replanned"] = True
            new_decision["replan_reason"] = (
                f"DYNAMIC REPLAN TRIGGERED: {evt_desc}. "
                f"Ambulance diverted from {previous_hospital} (prev score: {previous_score}) to {new_hospital} (new optimal score: {new_decision['score']}). "
                f"Contingency failover executed successfully."
            )
            # Update reason so frontend CAD banner highlights the dynamic reroute
            new_decision["reason"] = new_decision["replan_reason"]
            
        return new_decision
