"""Checks for the non-optimizing, reproducible schedule preparer."""

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_random_burning_input import prepare_parts, select_sources  # noqa: E402
from find_small_graph_burning_sequence import read_graph  # noqa: E402
from validate_burning_schedule import parse_lines  # noqa: E402


class RandomBurningInputTests(unittest.TestCase):
    def setUp(self):
        self.input_path = ROOT / "datasets" / "thirty-node-undirected-burning"
        self.graph = read_graph(self.input_path)

    def test_same_seed_repeats_sequence(self):
        expected = {1: 4, 2: 27, 3: 12, 4: 15}
        self.assertEqual(select_sources(self.graph, 4, 20261026), expected)
        self.assertEqual(select_sources(self.graph, 4, 20261026), expected)

    def test_generated_parts_keep_edges_and_are_valid(self):
        chosen = select_sources(self.graph, 4, 20261026)
        parts = prepare_parts(self.input_path, self.graph, chosen)
        parsed_graph, parsed_sources = parse_lines(
            line for content in parts.values() for line in content.splitlines()
        )
        self.assertEqual(len(parts), 3)
        self.assertEqual(len(parsed_graph), 30)
        self.assertEqual(sum(map(len, parsed_graph.values())) // 2, 55)
        self.assertEqual(parsed_graph, self.graph)
        self.assertEqual(parsed_sources, chosen)

    def test_invalid_round_count(self):
        with self.assertRaisesRegex(ValueError, "at least 1"):
            select_sources(self.graph, 0, 1)


if __name__ == "__main__":
    unittest.main()
