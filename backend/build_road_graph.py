import csv
import math
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "backend", "data")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c * 1.3, 2) # 1.3x road tortuosity

# Key Network Nodes (Pickup Zones & Arterial Junctions)
NODES = {
    "N0214": {"name": "Gandhipuram Central", "lat": 11.0168, "lon": 76.9673},
    "N0119": {"name": "Peelamedu Tech Zone", "lat": 11.0280, "lon": 77.0150},
    "N0050": {"name": "RS Puram West", "lat": 11.0080, "lon": 76.9450},
    "N0550": {"name": "Saravanampatti IT Corridor", "lat": 11.0820, "lon": 76.9950},
    "N0060": {"name": "Singanallur Trichy Rd", "lat": 11.0000, "lon": 77.0250},
    "N0800": {"name": "Thudiyalur North", "lat": 11.0850, "lon": 76.9400},
    "N0900": {"name": "Sundarapuram South", "lat": 10.9600, "lon": 76.9650},
    "N0150": {"name": "Ukkadam South Bus Stand", "lat": 10.9920, "lon": 76.9600},
    "N0473": {"name": "Neelambur Bypass", "lat": 11.0650, "lon": 77.0500},
    "N0355": {"name": "Saibaba Colony NSR Rd", "lat": 11.0290, "lon": 76.9480},
    # Intermediate Arterial Junctions
    "J_LAKSHMI": {"name": "Lakshmi Mills Junction", "lat": 11.0180, "lon": 76.9850},
    "J_HOPE_CLG": {"name": "Hope College Junction", "lat": 11.0250, "lon": 77.0080},
    "J_RAM_NAGAR": {"name": "Ram Nagar Cross Cut", "lat": 11.0180, "lon": 76.9600},
    "J_TOWN_HALL": {"name": "Town Hall Junction", "lat": 11.0010, "lon": 76.9620},
    "J_GANAPATHY": {"name": "Ganapathy Junction", "lat": 11.0420, "lon": 76.9780},
    "J_METTU_RD": {"name": "Mettupalayam Rd Junction", "lat": 11.0550, "lon": 76.9450},
    "J_TRICHY_RD": {"name": "Trichy Rd Flyover", "lat": 11.0020, "lon": 76.9900},
    "J_AIRPORT": {"name": "Airport Junction", "lat": 11.0330, "lon": 77.0420},
    "J_PODANUR": {"name": "Podanur Junction", "lat": 10.9700, "lon": 76.9800}
}

# Arterial Corridor Edges (Core Highway/Arterial Backbone)
CORRIDORS = [
    # Avinashi Road Corridor
    ("N0214", "J_LAKSHMI", 45),
    ("J_LAKSHMI", "J_HOPE_CLG", 45),
    ("J_HOPE_CLG", "N0119", 40),
    ("N0119", "J_AIRPORT", 50),
    ("J_AIRPORT", "N0473", 60),

    # Cross Cut & West Corridor
    ("N0214", "J_RAM_NAGAR", 35),
    ("J_RAM_NAGAR", "N0050", 40),
    ("N0050", "N0355", 40),
    ("N0355", "J_METTU_RD", 45),
    ("J_METTU_RD", "N0800", 50),

    # Sathy Road IT Corridor
    ("N0214", "J_GANAPATHY", 40),
    ("J_GANAPATHY", "N0550", 50),
    ("N0800", "N0550", 45),
    ("N0550", "N0473", 55),

    # South & Trichy Road Corridor
    ("N0214", "J_TOWN_HALL", 35),
    ("J_TOWN_HALL", "N0150", 40),
    ("N0150", "N0900", 50),
    ("N0150", "J_TRICHY_RD", 40),
    ("J_TRICHY_RD", "N0060", 45),
    ("N0060", "J_HOPE_CLG", 40),
    ("N0060", "J_AIRPORT", 45),
    ("N0900", "J_PODANUR", 40),
    ("J_PODANUR", "N0060", 40),

    # Cross connections / Detour bypasses
    ("J_LAKSHMI", "J_TRICHY_RD", 40),
    ("J_RAM_NAGAR", "J_GANAPATHY", 35),
    ("N0050", "J_TOWN_HALL", 35)
]

def main():
    roads = []
    road_id_counter = 1
    
    # 1. Add arterial backbone edges
    for u, v, speed in CORRIDORS:
        n1 = NODES[u]
        n2 = NODES[v]
        dist = haversine(n1["lat"], n1["lon"], n2["lat"], n2["lon"])
        roads.append({
            "road_id": f"R{road_id_counter:04d}",
            "from_node": u,
            "to_node": v,
            "distance_km": dist,
            "speed_kmh": speed,
            "status": "OPEN"
        })
        road_id_counter += 1

    # 2. Read hospitals and connect each to its 3 closest network nodes
    hospitals = []
    hosp_file = os.path.join(DATA_DIR, "hospitals.csv")
    with open(hosp_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hospitals.append({
                "id": row["hospital_id"],
                "name": row["name"],
                "lat": float(row.get("latitude", 11.0168)),
                "lon": float(row.get("longitude", 76.9673))
            })

    for h in hospitals:
        # Calculate distance to all NODES
        dists = []
        for n_id, n_data in NODES.items():
            d = haversine(h["lat"], h["lon"], n_data["lat"], n_data["lon"])
            dists.append((d, n_id))
        dists.sort()
        
        # Connect to the 2 closest nodes (primary access + alternate access)
        for d, n_id in dists[:2]:
            roads.append({
                "road_id": f"R{road_id_counter:04d}",
                "from_node": n_id,
                "to_node": h["id"],
                "distance_km": max(0.4, d),
                "speed_kmh": 35,
                "status": "OPEN"
            })
            road_id_counter += 1

    # Write out roads.csv
    roads_file = os.path.join(DATA_DIR, "roads.csv")
    with open(roads_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["road_id", "from_node", "to_node", "distance_km", "speed_kmh", "status"])
        for r in roads:
            writer.writerow([r["road_id"], r["from_node"], r["to_node"], r["distance_km"], r["speed_kmh"], r["status"]])

    print(f"Generated {len(roads)} road segments connecting {len(NODES)} zones and {len(hospitals)} hospitals.")

if __name__ == "__main__":
    main()
