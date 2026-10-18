"""Check the new teaching simulation, including the limit and safety errors."""

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "simulate_limited_neighbour_burning.py"
SPEC = importlib.util.spec_from_file_location(SCRIPT.stem, SCRIPT)
burning = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(burning)
DATA = ROOT / "datasets" / "limited-neighbour-burning-demo"


class LimitedNeighbourBurningTests(unittest.TestCase):
    def setUp(self):
        self.graph = burning.read_graph(DATA / "graph-parts")
        self.schedule = burning.read_schedule(DATA / "schedule-1-4-6.txt")

    def test_graph_and_schedule(self):
        self.assertEqual(len(self.graph), 8)
        self.assertEqual(self.graph[1], {2, 3, 7})
        self.assertEqual(self.schedule, [(1, [2, 3]), (4, [5]), (6, [])])

    def test_exact_result_and_round_trace(self):
        result, trace = burning.simulate(self.graph, self.schedule)
        self.assertEqual(result, {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 3, 7: -1, 8: -1})
        self.assertEqual([step[2] for step in trace], [2, 1, 0])
        self.assertEqual([step[4] for step in trace], [3, 5, 6])
        self.assertEqual(burning.result_lines(result)[-2:], ["7\tNB\t-1", "8\tNB\t-1"])

    def test_limit_is_enforced(self):
        with self.assertRaisesRegex(ValueError, "limit is 2"):
            burning.simulate(self.graph, [(1, [2, 3, 7]), (4, [5]), (6, [])])

    def test_non_adjacent_vertex_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not directly adjacent"):
            burning.simulate(self.graph, [(1, [4]), (4, [5]), (6, [])])

    def test_already_burned_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "already burned"):
            burning.simulate(self.graph, [(1, [2]), (2, [4])])

    def test_no_automatic_propagation(self):
        result, _ = burning.simulate(self.graph, self.schedule)
        # Vertex 7 touches burned vertex 1, but it was not chosen by 1.
        # Vertex 8 touches burned vertices 4 and 6; neither selected it.
        self.assertEqual((result[7], result[8]), (-1, -1))

    def test_missing_reverse_edge_is_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "graph.txt"
            path.write_text("1 2:1\n2\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "reverse entry"):
                burning.read_graph(path)


if __name__ == "__main__":
    unittest.main()
