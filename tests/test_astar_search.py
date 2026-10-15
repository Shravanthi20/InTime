import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from agents.mobility_agent import MobilityAgent

class TestAStarSearch(unittest.TestCase):
    def setUp(self):
        self.agent = MobilityAgent()

    def test_admissible_heuristic(self):
        """Verify h(n) <= true remaining road time h*(n) (Admissibility condition)."""
        start = "N0214"
        goal = "H001"
        h_val = self.agent.heuristic(start, goal)
        search_res = self.agent.a_star_search(start, goal)
        actual_time = search_res["travel_time_min"]
        
        # h(n) must never overestimate the actual time
        self.assertLessEqual(h_val, actual_time, f"Heuristic {h_val} exceeds actual {actual_time}")

    def test_astar_finds_path(self):
        res = self.agent.a_star_search("N0214", "H004")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertGreater(len(res["path"]), 1)
        self.assertEqual(res["path"][0], "N0214")
        self.assertEqual(res["path"][-1], "H004")
        self.assertGreater(res["distance_km"], 0.0)
        self.assertGreater(res["travel_time_min"], 0.0)

    def test_astar_efficiency_vs_ucs(self):
        """Verify A* expands fewer or equal nodes compared to Uniform Cost Search (Dijkstra)."""
        benchmark = self.agent.compare_search_strategies("N0214", "H004")
        astar_nodes = benchmark["a_star"]["nodes_expanded"]
        ucs_nodes = benchmark["uniform_cost_search"]["nodes_expanded"]
        self.assertLessEqual(astar_nodes, ucs_nodes)

    def test_astar_rerouting_on_blockage(self):
        """When an intermediate node or corridor is blocked, A* finds an alternative detour."""
        normal_res = self.agent.a_star_search("N0214", "H003")
        # Block an intermediate junction in that route
        blocked_node = normal_res["path"][1] if len(normal_res["path"]) > 2 else "J_LAKSHMI"
        rerouted_res = self.agent.a_star_search("N0214", "H003", blocked_nodes_or_hospitals=[blocked_node])
        
        self.assertEqual(rerouted_res["status"], "SUCCESS")
        # The rerouted path must avoid the blocked node
        self.assertNotIn(blocked_node, rerouted_res["path"])

if __name__ == "__main__":
    unittest.main()
