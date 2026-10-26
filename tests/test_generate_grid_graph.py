"""Small hand-checkable tests for the split undirected grid generator."""

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_grid_graph import make_grid, split_parts  # noqa: E402


class GridGraphTests(unittest.TestCase):
    def test_two_by_three_topology(self):
        graph = make_grid(2, 3)
        self.assertEqual(graph, {
            1: [2, 4], 2: [1, 3, 5], 3: [2, 6],
            4: [1, 5], 5: [2, 4, 6], 6: [3, 5],
        })
        self.assertEqual(sum(map(len, graph.values())) // 2, 7)

    def test_each_vertex_occurs_once_across_parts(self):
        parts = split_parts(make_grid(2, 3), 3)
        ids = [int(line.split()[0]) for part in parts for line in part.splitlines()]
        self.assertEqual(ids, [1, 2, 3, 4, 5, 6])

    def test_reject_invalid_dimensions_or_part_count(self):
        with self.assertRaisesRegex(ValueError, "at least 2"):
            make_grid(1, 3)
        with self.assertRaisesRegex(ValueError, "between 1"):
            split_parts(make_grid(2, 2), 5)


if __name__ == "__main__":
    unittest.main()
