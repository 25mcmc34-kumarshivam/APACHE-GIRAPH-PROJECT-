"""Check the committed 120-node dataset and its saved Python prediction."""

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from find_small_graph_burning_sequence import read_graph  # noqa: E402
from validate_burning_schedule import parse_lines, predicted_rounds  # noqa: E402


class Grid120BurningTests(unittest.TestCase):
    def test_topology_and_scheduled_input_agree(self):
        original = read_graph(ROOT / "datasets" / "grid-120-unscheduled")
        folder = ROOT / "datasets" / "grid-120-random-burning-seed-20261026"
        parts = sorted(folder.glob("part-*.txt"))
        scheduled, sources = parse_lines(
            line for part in parts for line in part.read_text(encoding="utf-8").splitlines()
        )
        self.assertEqual(len(parts), 4)
        self.assertEqual(len(original), 120)
        self.assertEqual(sum(map(len, original.values())) // 2, 218)
        self.assertEqual(scheduled, {vertex: set(neighbours) for vertex, neighbours in original.items()})
        self.assertEqual(sources, {1: 15, 2: 104, 3: 35, 4: 101,
                                   5: 41, 6: 111, 7: 83, 8: 86})
        actual_prediction = predicted_rounds(scheduled, sources)
        self.assertEqual([v for v, r in actual_prediction.items() if r == -1], [85])
        saved = (ROOT / "results" / "grid-120-random-burning-seed-20261026"
                 / "python-preview" / "expected.tsv").read_text(encoding="utf-8")
        expected = "".join(
            "{}\t{}\t{}\n".format(v, "B" if actual_prediction[v] > 0 else "NB", actual_prediction[v])
            for v in sorted(scheduled)
        )
        self.assertEqual(saved, expected)


if __name__ == "__main__":
    unittest.main()
