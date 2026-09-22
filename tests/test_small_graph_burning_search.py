"""Small regression tests for the local exact Graph Burning checker."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "find_small_graph_burning_sequence.py"
SPEC = importlib.util.spec_from_file_location("burning_search", SCRIPT)
burning_search = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(burning_search)


class SmallGraphBurningSearchTests(unittest.TestCase):
    def assert_rounds(self, graph_path, expected_rounds):
        graph = burning_search.read_graph(ROOT / graph_path)
        sequence, _ = burning_search.find_sequence(graph)
        self.assertEqual(len(sequence), expected_rounds)
        self.assertEqual(len(set(sequence)), len(sequence))

    def test_nine_vertex_path_needs_three_rounds(self):
        self.assert_rounds("datasets/graph-burning-path-9", 3)

    def test_seven_vertex_star_needs_two_rounds(self):
        self.assert_rounds("datasets/graph-burning-star-7/graph.txt", 2)

    def test_two_disconnected_paths_need_three_rounds(self):
        self.assert_rounds("datasets/graph-burning-disconnected-6/graph.txt", 3)

    def test_rejects_edge_missing_its_reverse(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "graph.txt"
            path.write_text("1 2:1\n2\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not listed in reverse"):
                burning_search.read_graph(path)

    def test_rejects_duplicate_vertex_lines_across_parts(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "one.txt").write_text("1\n", encoding="utf-8")
            Path(directory, "two.txt").write_text("1\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "defined twice"):
                burning_search.read_graph(Path(directory))

    def test_state_limit_never_claims_an_exact_answer(self):
        graph = burning_search.read_graph(
            ROOT / "datasets/graph-burning-path-9"
        )
        with self.assertRaises(burning_search.SearchLimitReached):
            burning_search.find_sequence(graph, max_states=1)


if __name__ == "__main__":
    unittest.main()
