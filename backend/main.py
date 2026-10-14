from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import csv
import os
import shutil
import random

from agents.triage_agent import TriageAgent
from agents.hospital_agent import HospitalAgent
from agents.mobility_agent import MobilityAgent
from agents.coordination_agent import CoordinationAgent

app = FastAPI(title="InTime Multi-Agent Care Coordination API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

PICKUP_LOCATIONS = {
    "GANDHIPURAM": {
        "id": "GANDHIPURAM",
        "name": "Gandhipuram (Central Bus Stand)",
        "node": "N0214",
        "lat": 11.0168,
        "lon": 76.9673
    },
    "PEELAMEDU": {
        "id": "PEELAMEDU",
        "name": "Peelamedu (Avinashi Rd / Tech Zone)",
        "node": "N0119",
        "lat": 11.0280,
        "lon": 77.0150
    },
    "RS_PURAM": {
        "id": "RS_PURAM",
        "name": "RS Puram (West Coimbatore)",
        "node": "N0050",
        "lat": 11.0080,
        "lon": 76.9450
    },
    "SARAVANAMPATTI": {
        "id": "SARAVANAMPATTI",
        "name": "Saravanampatti (IT Corridor)",
        "node": "N0550",
        "lat": 11.0820,
        "lon": 76.9950
    },
    "SINGANALLUR": {
        "id": "SINGANALLUR",
        "name": "Singanallur (Trichy Rd)",
        "node": "N0060",
        "lat": 11.0000,
        "lon": 77.0250
    },
    "THUDIYALUR": {
        "id": "THUDIYALUR",
        "name": "Thudiyalur (Mettupalayam Rd)",
        "node": "N0800",
        "lat": 11.0850,
        "lon": 76.9400
    },
    "SUNDARAPURAM": {
        "id": "SUNDARAPURAM",
        "name": "Sundarapuram (Pollachi Rd)",
        "node": "N0900",
        "lat": 10.9600,
        "lon": 76.9650
    },
    "UKKADAM": {
        "id": "UKKADAM",
        "name": "Ukkadam (South City)",
        "node": "N0150",
        "lat": 10.9920,
        "lon": 76.9600
    },
    "NEELAMBUR": {
        "id": "NEELAMBUR",
        "name": "Neelambur (Bypass / Airport Outer)",
        "node": "N0473",
        "lat": 11.0650,
        "lon": 77.0500
    },
    "SAIBABA_COLONY": {
        "id": "SAIBABA_COLONY",
        "name": "Saibaba Colony (North-West)",
        "node": "N0355",
        "lat": 11.0290,
        "lon": 76.9480
    }
}

def read_hospitals():
    hospitals = {}
    with open(os.path.join(DATA_DIR, "hospitals.csv"), "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hospitals[row["hospital_id"]] = {
                "hospital_id": row["hospital_id"],
                "name": row["name"],
                "type": row["type"],
                "latitude": float(row.get("latitude", 11.0168)),
                "longitude": float(row.get("longitude", 76.9673)),
                "trauma_capability": row.get("trauma_capability") == "True",
                "specialists_available": row.get("specialists", "").split("|"),
                "ct_scan": row.get("ct_scan") == "True"
            }
            
    with open(os.path.join(DATA_DIR, "hospital_status.csv"), "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hid = row["hospital_id"]
            if hid in hospitals:
                hospitals[hid]["icu_available"] = int(row.get("icu_available", 0))
                hospitals[hid]["er_occupancy"] = float(row.get("er_occupancy", 0.5))
    return hospitals

def write_hospital_status(hospitals):
    with open(os.path.join(DATA_DIR, "hospital_status.csv"), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["hospital_id", "timestamp", "icu_available", "er_occupancy"])
        for hid, data in hospitals.items():
            writer.writerow([hid, time.strftime("%H:%M"), data.get("icu_available", 0), data.get("er_occupancy", 0.5)])

def restore_baseline_hospital_status():
    baseline_path = os.path.join(DATA_DIR, "hospital_status_baseline.csv")
    target_path = os.path.join(DATA_DIR, "hospital_status.csv")
    if os.path.exists(baseline_path):
        shutil.copy(baseline_path, target_path)

def read_events():
    events = []
    if os.path.exists(os.path.join(DATA_DIR, "events.csv")):
        with open(os.path.join(DATA_DIR, "events.csv"), "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                events.append(row)
    return events

def append_event(evt_type, target_id, desc):
    with open(os.path.join(DATA_DIR, "events.csv"), "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([evt_type, target_id, desc, time.strftime("%H:%M:%S")])

def clear_events():
    with open(os.path.join(DATA_DIR, "events.csv"), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["type", "target_id", "desc", "time"])

def read_patient():
    if not os.path.exists(os.path.join(DATA_DIR, "patients.csv")):
        return {
            "id": "P1001",
            "timestamp": time.strftime("%H:%M"),
            "emergency_type": "SEVERE_TRAUMA",
            "severity": "CRITICAL",
            "spo2": 88,
            "heart_rate": 85,
            "consciousness": "ALERT",
            "pickup_location": "GANDHIPURAM",
            "pickup_name": PICKUP_LOCATIONS["GANDHIPURAM"]["name"],
            "pickup_node": PICKUP_LOCATIONS["GANDHIPURAM"]["node"],
            "latitude": PICKUP_LOCATIONS["GANDHIPURAM"]["lat"],
            "longitude": PICKUP_LOCATIONS["GANDHIPURAM"]["lon"]
        }
        
    with open(os.path.join(DATA_DIR, "patients.csv"), "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            loc_key = row.get("pickup_location") or "GANDHIPURAM"
            if loc_key not in PICKUP_LOCATIONS:
                loc_key = "GANDHIPURAM"
            loc_info = PICKUP_LOCATIONS[loc_key]
            
            return {
                "id": row.get("id", "P1001"),
                "timestamp": row.get("timestamp", time.strftime("%H:%M")),
                "emergency_type": row.get("emergency_type", "SEVERE_TRAUMA"),
                "severity": row.get("severity", "CRITICAL"),
                "spo2": int(row.get("spo2", 95)),
                "heart_rate": int(row.get("heart_rate", 80)),
                "consciousness": row.get("consciousness", "ALERT"),
                "pickup_location": loc_key,
                "pickup_name": loc_info["name"],
                "pickup_node": loc_info["node"],
                "latitude": loc_info["lat"],
                "longitude": loc_info["lon"]
            }

# Initialize Multi-Agent System
agent1_triage = TriageAgent()
agent3_mobility = MobilityAgent()
agent4_coordinator = CoordinationAgent()

class EventPayload(BaseModel):
    event_type: str
    target_id: str = None
    
class PatientPayload(BaseModel):
    emergency_type: str
    severity: str
    spo2: int
    pickup_location: str = "GANDHIPURAM"
    heart_rate: int = 80
    consciousness: str = "ALERT"

@app.get("/api/state")
def get_state():
    hospitals = read_hospitals()
    patient = read_patient()
    events = read_events()
    
    agent2_hospital = HospitalAgent(hospitals)
    
    # 1. Triage Agent (Requirement Extraction)
    reqs = agent1_triage.evaluate_patient(patient)
    
    # 2. Hospital Agent (Constraint Satisfaction)
    feasibility = agent2_hospital.find_feasible_hospitals(reqs)
    feasible_list = feasibility["feasible_hospitals"]
    
    # 3. Mobility Agent (Geographic Routing)
    patient_coords = (patient["latitude"], patient["longitude"])
    routes = agent3_mobility.calculate_routes(
        patient_coords=patient_coords, 
        candidate_hospitals=feasible_list,
        active_events=events
    )
    
    # 4. Coordination Agent (Optimization & Allocation)
    allocation = agent4_coordinator.allocate(reqs, routes, hospitals)
    
    return {
        "patient": patient,
        "hospitals": hospitals,
        "events": events,
        "pickup_locations": list(PICKUP_LOCATIONS.values()),
        "agent1_triage": reqs,
        "agent2_hospital": feasibility,
        "agent3_mobility": routes,
        "agent4_coordination": allocation
    }

@app.post("/api/new_patient")
def new_patient(payload: PatientPayload):
    new_id = f"P{random.randint(1000, 9999)}"
    loc_key = payload.pickup_location if payload.pickup_location in PICKUP_LOCATIONS else "GANDHIPURAM"
    loc_info = PICKUP_LOCATIONS[loc_key]
    
    with open(os.path.join(DATA_DIR, "patients.csv"), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "timestamp", "emergency_type", "severity", "spo2", "pickup_location", "heart_rate", "consciousness"])
        writer.writerow([new_id, time.strftime("%H:%M"), payload.emergency_type, payload.severity, payload.spo2, loc_key, payload.heart_rate, payload.consciousness])
        
    clear_events()
    append_event("NEW_PATIENT", new_id, f"Dispatched for {payload.emergency_type} ({payload.severity}) at {loc_info['name']}")
    return get_state()

@app.post("/api/trigger_event")
def trigger_event(payload: EventPayload):
    hospitals = read_hospitals()
    
    if payload.event_type == "RESET":
        clear_events()
        restore_baseline_hospital_status()
        return get_state()
        
    # Get current winning hospital to apply realistic dynamic disruption
    current_state = get_state()
    assigned_h_id = "H001"
    assigned_h_name = "Assigned Hospital"
    if current_state.get("agent4_coordination", {}).get("assigned_hospital"):
        assigned_h_id = current_state["agent4_coordination"]["assigned_hospital"]
        assigned_h_name = current_state["agent4_coordination"]["assigned_hospital_name"]
        
    if payload.event_type == "HOSPITAL_FULL":
        if assigned_h_id in hospitals:
            hospitals[assigned_h_id]["icu_available"] = 0
            write_hospital_status(hospitals)
            append_event("CAPACITY_CHANGE", assigned_h_id, f"{assigned_h_name} ICU beds became completely full")
        
    elif payload.event_type == "ROAD_CLOSED":
        append_event("ROAD_BLOCK", assigned_h_id, f"Major accident & road blockage on primary route to {assigned_h_name}")
        
    return get_state()
