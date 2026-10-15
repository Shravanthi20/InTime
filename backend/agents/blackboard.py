import time
from typing import Dict, List, Any

class Blackboard:
    """
    Multi-Agent Coordination Blackboard
    Acts as the centralized shared workspace and message bus for the autonomous agent swarm.
    Follows the classic Hearsay-II blackboard pattern for cooperative problem solving.
    """
    def __init__(self):
        self.state: Dict[str, Any] = {
            "patient_case": None,
            "triage_evaluation": None,
            "feasible_hospitals": [],
            "mobility_routes": [],
            "ambulance_assignment": None,
            "coordination_decision": None,
            "active_disruptions": []
        }
        self.message_bus: List[Dict[str, Any]] = []

    def publish_message(self, sender: str, channel: str, message: str, payload: Any = None):
        """Broadcasts an agent message to the blackboard message log."""
        timestamp = time.strftime("%H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "sender": sender,
            "channel": channel,
            "message": message,
            "payload_summary": str(payload)[:120] if payload else None
        }
        self.message_bus.append(entry)
        return entry

    def update_state(self, key: str, value: Any, sender: str, message: str):
        """Updates a blackboard knowledge partition and logs the agent transition."""
        self.state[key] = value
        self.publish_message(sender=sender, channel=key, message=message, payload=value)

    def get_state(self, key: str = None):
        if key:
            return self.state.get(key)
        return self.state

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return self.message_bus

    def clear(self):
        self.__init__()
