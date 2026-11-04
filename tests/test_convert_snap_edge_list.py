import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from convert_snap_edge_list import largest_component, read_undirected_edges, write_parts


class SnapConversionTests(unittest.TestCase):
    def test_comments_duplicates_self_loops_and_component(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "edges.txt"
            source.write_text("# header\n0 1\n1 0\n1 1\n2 3\n", encoding="utf-8")
            graph = largest_component(read_undirected_edges(source, 10))
            self.assertEqual(graph, {0: {1}, 1: {0}})

    def test_parts_use_adjacency_format(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "parts"
            write_parts({0: {1}, 1: {0, 2}, 2: {1}}, output, 2)
            self.assertEqual((output / "part-01.txt").read_text(), "0 1:1\n1 0:1 2:1\n")
            self.assertEqual((output / "part-02.txt").read_text(), "2 1:1\n")


if __name__ == "__main__":
    unittest.main()
