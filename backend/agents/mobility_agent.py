import math

class MobilityAgent:
    """
    Person 3: Mobility & Routing Agent
    Core AI: Geographic Distance Calculation & Traffic Dynamic Routing Engine
    """
    def __init__(self, road_network: dict = None):
        self.road_network = road_network or {}
        
    def calculate_routes(self, patient_coords: tuple, candidate_hospitals: list, active_events: list = None) -> list:
        active_events = active_events or []
        routes = []
        p_lat, p_lon = patient_coords
        
        for h in candidate_hospitals:
            h_lat = float(h.get("latitude", 11.0168))
            h_lon = float(h.get("longitude", 76.9673))
            
            # Accurate Haversine road distance in kilometers
            road_dist = self._haversine_distance_km(p_lat, p_lon, h_lat, h_lon)
            
            # Realistic ambulance travel time: avg city speed 32 km/h + 1.5 min dispatch/maneuver
            base_eta = round(1.5 + (road_dist / 32.0) * 60.0, 1)
            
            traffic_multiplier = 1.0
            traffic_reason = "Normal arterial flow"
            
            # Evaluate real-time traffic events
            for event in active_events:
                if event.get("type") == "ROAD_BLOCK" and h["hospital_id"] in event.get("target_id", ""):
                    traffic_multiplier = 2.4
                    traffic_reason = "Severe corridor blockage: Re-routing via outer ring road (+140% delay)"
                elif event.get("type") == "ROAD_CONGESTION" and h["hospital_id"] in event.get("target_id", ""):
                    traffic_multiplier = 1.5
                    traffic_reason = "Heavy peak-hour congestion along route (+50% delay)"
                    
            actual_eta = round(base_eta * traffic_multiplier, 1)
            
            routes.append({
                "hospital_id": h["hospital_id"],
                "name": h["name"],
                "base_eta_min": base_eta,
                "actual_eta_min": actual_eta,
                "distance_km": road_dist,
                "route_status": "DELAYED" if traffic_multiplier > 1.0 else "OPTIMAL",
                "reason": f"{road_dist} km transit (~{base_eta} min base). {traffic_reason}."
            })
            
        return sorted(routes, key=lambda x: x["actual_eta_min"])

    def _haversine_distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0 # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2.0)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        # Urban road tortuosity factor (~1.35x straight line)
        dist = R * c * 1.35
        return round(max(0.8, dist), 1)
