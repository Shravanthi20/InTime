from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import csv
import os
import random

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from agents.triage_agent import TriageAgent
from agents.hospital_agent import HospitalAgent
from agents.mobility_agent import MobilityAgent
from agents.coordination_agent import CoordinationAgent
from agents.ambulance_agent import AmbulanceAgent
from agents.blackboard import Blackboard

app = FastAPI(
    title="InTime Multi-Agent Care Coordination API",
    description="Decentralized multi-agent architecture for autonomous emergency dispatch, A* routing, and hospital allocation"
)

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

def load_initial_hospitals():
    """Loads baseline hospital data into in-memory state."""
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
            
    # Read baseline status
    status_file = os.path.join(DATA_DIR, "hospital_status_baseline.csv")
    if not os.path.exists(status_file):
        status_file = os.path.join(DATA_DIR, "hospital_status.csv")
        
    with open(status_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hid = row["hospital_id"]
            if hid in hospitals:
                hospitals[hid]["icu_available"] = int(row.get("icu_available", 0))
                hospitals[hid]["er_occupancy"] = float(row.get("er_occupancy", 0.5))
    return hospitals

def get_default_patient():
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

# Autonomous Multi-Agent Swarm Instances
blackboard = Blackboard()
agent1_triage = TriageAgent()
agent3_mobility = MobilityAgent()
agent4_coordinator = CoordinationAgent()
agent5_ambulance = AmbulanceAgent()

# In-Memory Active Operational State (prevents file corruptions and git dirt)
OPERATIONAL_STATE = {
    "hospitals": load_initial_hospitals(),
    "patient": get_default_patient(),
    "events": [],
    "last_assignment": None
}

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

def run_agent_swarm(is_replan=False, disruption_event=None):
    """
    Executes the multi-agent problem-solving cycle via the shared Blackboard:
    1. Triage Agent: Evaluates patient vitals & generates clinical requirement constraints.
    2. Hospital Agent: Solves Constraint Satisfaction Problem (CSP) for clinical feasibility.
    3. Mobility Agent: Executes A* Heuristic Search on Coimbatore road graph.
    4. Ambulance Agent: Runs Contract Net Protocol (CNP) for fleet bidding & vehicle allocation.
    5. Coordination Agent: Computes Multi-Objective Loss Optimization & standby contingencies.
    """
    patient = OPERATIONAL_STATE["patient"]
    hospitals = OPERATIONAL_STATE["hospitals"]
    events = OPERATIONAL_STATE["events"]
    pickup_node = patient["pickup_node"]
    patient_coords = (patient["latitude"], patient["longitude"])
    
    agent2_hospital = HospitalAgent(hospitals)
    
    # --- Agent 1: Triage Agent ---
    reqs = agent1_triage.evaluate_patient(patient)
    blackboard.update_state(
        key="triage_evaluation",
        value=reqs,
        sender="TriageAgent",
        message=f"Triaged patient {patient['id']} as {reqs['priority']} priority (Time sensitivity: {reqs['time_sensitivity']})"
    )
    
    # --- Agent 2: Hospital Capability Agent (CSP) ---
    feasibility = agent2_hospital.find_feasible_hospitals(reqs)
    feasible_list = feasibility["feasible_hospitals"]
    blackboard.update_state(
        key="feasible_hospitals",
        value=feasible_list,
        sender="HospitalAgent",
        message=f"Constraint Satisfaction: {len(feasible_list)}/{len(hospitals)} facilities passed ICU, CT, and specialist constraints"
    )
    
    # --- Agent 3: Mobility & Routing Agent (A* Graph Search) ---
    routes = agent3_mobility.calculate_routes(
        patient_coords=patient_coords,
        candidate_hospitals=feasible_list,
        active_events=events,
        pickup_node=pickup_node
    )
    blackboard.update_state(
        key="mobility_routes",
        value=routes,
        sender="MobilityAgent",
        message=f"A* Search computed optimal road paths for {len(routes)} candidates using admissible Haversine heuristic"
    )
    
    # --- Agent 5: Ambulance Fleet Allocation (Contract Net Protocol) ---
    ambulance_award = agent5_ambulance.contract_net_bidding(
        patient_reqs=reqs,
        pickup_node=pickup_node,
        mobility_agent=agent3_mobility
    )
    blackboard.update_state(
        key="ambulance_assignment",
        value=ambulance_award,
        sender="AmbulanceAgent",
        message=f"Contract Net Protocol: Unit {ambulance_award.get('assigned_ambulance')} awarded contract (ETA: {ambulance_award.get('response_eta_min')} min)"
    )
    
    # --- Agent 4: Coordination & Allocation Agent ---
    if is_replan and disruption_event and OPERATIONAL_STATE["last_assignment"]:
        # Execute dynamic contingency failover
        allocation = agent4_coordinator.handle_event_and_replan(
            event=disruption_event,
            current_assignment=OPERATIONAL_STATE["last_assignment"],
            all_agents_re_eval={
                "reqs": reqs,
                "routes": routes,
                "hospitals_status": hospitals
            }
        )
        blackboard.publish_message(
            sender="CoordinationAgent",
            channel="replan_failover",
            message=f"DYNAMIC REPLAN: Diverted ambulance to {allocation.get('assigned_hospital_name')}",
            payload=allocation
        )
    else:
        allocation = agent4_coordinator.allocate(reqs, routes, hospitals)
        blackboard.update_state(
            key="coordination_decision",
            value=allocation,
            sender="CoordinationAgent",
            message=f"Allocated to {allocation.get('assigned_hospital_name')} (Loss Score: {allocation.get('score')})"
        )
        
    OPERATIONAL_STATE["last_assignment"] = allocation
    
    # Strategy benchmark comparison for examiners / review
    target_hid = allocation.get("assigned_hospital") or "H001"
    search_benchmark = agent3_mobility.compare_search_strategies(pickup_node, target_hid)
    
    return {
        "patient": patient,
        "hospitals": hospitals,
        "events": events,
        "pickup_locations": list(PICKUP_LOCATIONS.values()),
        "agent1_triage": reqs,
        "agent2_hospital": feasibility,
        "agent3_mobility": routes,
        "agent4_coordination": allocation,
        "agent5_ambulance": ambulance_award,
        "blackboard_audit": blackboard.get_audit_trail()[-10:], # Last 10 inter-agent events
        "search_benchmark": search_benchmark
    }

@app.get("/api/state")
def get_state():
    return run_agent_swarm(is_replan=False)

@app.post("/api/new_patient")
def new_patient(payload: PatientPayload):
    new_id = f"P{random.randint(1000, 9999)}"
    loc_key = payload.pickup_location if payload.pickup_location in PICKUP_LOCATIONS else "GANDHIPURAM"
    loc_info = PICKUP_LOCATIONS[loc_key]
    
    OPERATIONAL_STATE["patient"] = {
        "id": new_id,
        "timestamp": time.strftime("%H:%M"),
        "emergency_type": payload.emergency_type,
        "severity": payload.severity,
        "spo2": payload.spo2,
        "heart_rate": payload.heart_rate,
        "consciousness": payload.consciousness,
        "pickup_location": loc_key,
        "pickup_name": loc_info["name"],
        "pickup_node": loc_info["node"],
        "latitude": loc_info["lat"],
        "longitude": loc_info["lon"]
    }
    
    OPERATIONAL_STATE["events"] = []
    blackboard.clear()
    
    event_entry = {
        "type": "NEW_PATIENT",
        "target_id": new_id,
        "desc": f"Dispatched for {payload.emergency_type} ({payload.severity}) at {loc_info['name']}",
        "time": time.strftime("%H:%M:%S")
    }
    OPERATIONAL_STATE["events"].append(event_entry)
    blackboard.publish_message("Dispatcher", "intake", event_entry["desc"], event_entry)
    
    return run_agent_swarm(is_replan=False)

@app.post("/api/trigger_event")
def trigger_event(payload: EventPayload):
    if payload.event_type == "RESET":
        OPERATIONAL_STATE["hospitals"] = load_initial_hospitals()
        OPERATIONAL_STATE["events"] = []
        OPERATIONAL_STATE["last_assignment"] = None
        blackboard.clear()
        return run_agent_swarm(is_replan=False)
        
    # Get current winning hospital to apply realistic dynamic disruption
    current_assignment = OPERATIONAL_STATE.get("last_assignment")
    if not current_assignment:
        current_state = run_agent_swarm(is_replan=False)
        current_assignment = current_state.get("agent4_coordination")
        
    assigned_h_id = current_assignment.get("assigned_hospital", "H001")
    assigned_h_name = current_assignment.get("assigned_hospital_name", "Primary Facility")
    
    event_entry = None
    if payload.event_type == "HOSPITAL_FULL":
        if assigned_h_id in OPERATIONAL_STATE["hospitals"]:
            OPERATIONAL_STATE["hospitals"][assigned_h_id]["icu_available"] = 0
            event_entry = {
                "type": "CAPACITY_CHANGE",
                "target_id": assigned_h_id,
                "desc": f"{assigned_h_name} ICU beds became completely full (0 beds)",
                "time": time.strftime("%H:%M:%S")
            }
            OPERATIONAL_STATE["events"].append(event_entry)
            blackboard.publish_message("HospitalSensor", "icu_saturation", event_entry["desc"], event_entry)
            
    elif payload.event_type == "ROAD_CLOSED":
        event_entry = {
            "type": "ROAD_BLOCK",
            "target_id": assigned_h_id,
            "desc": f"Major multi-vehicle collision & road blockage on primary corridor to {assigned_h_name}",
            "time": time.strftime("%H:%M:%S")
        }
        OPERATIONAL_STATE["events"].append(event_entry)
        blackboard.publish_message("TrafficSensor", "road_blockage", event_entry["desc"], event_entry)
        
    # Trigger multi-agent reactive replanning!
    return run_agent_swarm(is_replan=True, disruption_event=event_entry)
