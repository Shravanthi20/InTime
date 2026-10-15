import csv
import os
import math
from typing import Dict, List, Any

class AmbulanceAgent:
    """
    Agent 5: Ambulance Fleet Allocation Agent
    Core AI: Contract Net Protocol (CNP) Market-Based Negotiation & Capability Bidding.
    Manages fleet allocation, vehicle type matching (ALS vs BLS), and response dispatch.
    """
    def __init__(self, ambulances_csv_path: str = None):
        self.csv_path = ambulances_csv_path or os.path.join(os.path.dirname(__file__), "..", "data", "ambulances.csv")
        self.fleet = self._load_fleet()

    def _load_fleet(self) -> List[Dict[str, Any]]:
        fleet = []
        if os.path.exists(self.csv_path):
            with open(self.csv_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fleet.append({
                        "ambulance_id": row["ambulance_id"],
                        "type": row.get("type", "BLS"),
                        "current_node": row.get("current_node", "N0214"),
                        "base_name": row.get("base_name", "Central Station"),
                        "status": row.get("status", "AVAILABLE"),
                        "driver": row.get("driver", "Duty Crew"),
                        "equipment": row.get("equipment", "O2|FIRST_AID").split("|")
                    })
        return fleet

    def contract_net_bidding(self, patient_reqs: dict, pickup_node: str, mobility_agent=None) -> dict:
        """
        Executes Contract Net Protocol (Smith, 1980):
        1. Manager issues Call For Proposals (CFP) specifying patient severity & pickup node.
        2. Available ambulances submit bids based on equipment capability and ETA.
        3. Manager evaluates bids and awards the dispatch contract.
        """
        time_sensitivity = patient_reqs.get("time_sensitivity", "NORMAL")
        required_type = "ALS" if time_sensitivity == "CRITICAL" else "BLS"
        
        bids = []
        for amb in self.fleet:
            if amb["status"] != "AVAILABLE":
                continue
                
            # Capability check: Critical emergencies strictly require Advanced Life Support (ALS)
            if required_type == "ALS" and amb["type"] != "ALS":
                continue
                
            # Compute transit from ambulance station node to patient pickup node
            transit_eta = 3.0 # Default base
            distance_km = 2.0
            
            if mobility_agent and amb["current_node"] != pickup_node:
                search_res = mobility_agent.a_star_search(amb["current_node"], pickup_node)
                transit_eta = search_res.get("travel_time_min", 4.0)
                distance_km = search_res.get("distance_km", 2.5)
            elif amb["current_node"] == pickup_node:
                transit_eta = 1.0 # On-site or adjacent
                distance_km = 0.5
                
            # Bid score: lower ETA is better; slight bonus for matching equipment
            bid_score = round(transit_eta * 1.0 + distance_km * 0.2, 2)
            
            bids.append({
                "ambulance_id": amb["ambulance_id"],
                "type": amb["type"],
                "base_name": amb["base_name"],
                "current_node": amb["current_node"],
                "driver": amb["driver"],
                "equipment": amb["equipment"],
                "transit_eta_min": transit_eta,
                "distance_km": distance_km,
                "bid_score": bid_score
            })
            
        if not bids:
            # Fallback if no matching unit free
            return {
                "status": "FAILED",
                "reason": f"No available {required_type} ambulances in operational sector.",
                "assigned_ambulance": None,
                "all_bids": []
            }
            
        # Select winning bid (lowest score = fastest response)
        bids.sort(key=lambda x: x["bid_score"])
        winner = bids[0]
        
        return {
            "status": "ASSIGNED",
            "protocol": "Contract Net Protocol (CNP)",
            "assigned_ambulance": winner["ambulance_id"],
            "type": winner["type"],
            "driver": winner["driver"],
            "base_name": winner["base_name"],
            "station_node": winner["current_node"],
            "response_eta_min": winner["transit_eta_min"],
            "equipment": winner["equipment"],
            "winning_bid_score": winner["bid_score"],
            "competing_bids": bids[1:],
            "rationale": f"Contract awarded to unit {winner['ambulance_id']} ({winner['type']} certified, {winner['driver']}) stationed at {winner['base_name']} with response ETA {winner['transit_eta_min']} min."
        }
