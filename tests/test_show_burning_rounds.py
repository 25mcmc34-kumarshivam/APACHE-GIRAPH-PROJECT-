"""Tests for the round-by-round preview of a supplied burning schedule."""

from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import show_burning_rounds as preview  # noqa: E402
from validate_burning_schedule import parse_lines  # noqa: E402


class RoundPreviewTests(unittest.TestCase):
    def test_first_round_has_only_its_source(self):
        graph, sources = preview.load_input(
            ROOT / "datasets" / "graph-burning-path-9-scheduled"
        )
        history, actual = preview.simulate_rounds(graph, sources)
        self.assertEqual(sources, {1: 3, 2: 8, 3: 6})
        self.assertEqual(history[0][2], [3])
        self.assertEqual(history[1][2], [2, 4, 8])
        self.assertEqual(history[2][2], [1, 5, 6, 7, 9])
        self.assertEqual(actual[3], 1)
        self.assertEqual(actual[2], 2)

    def test_round_two_spreads_old_fire_and_ignites_new_source(self):
        graph, sources = preview.load_input(
            ROOT / "datasets" / "graph-burning-path-9-two-round-scheduled"
        )
        history, actual = preview.simulate_rounds(graph, sources)
        self.assertEqual(history[0][2], [2])
        self.assertEqual(history[0][4], [])  # A one-node subgraph has no edge.
        self.assertEqual(history[1][2], [1, 3, 8])
        self.assertEqual(history[1][4], [(1, 2), (2, 3)])
        self.assertEqual(actual[4], -1)

    def test_one_four_six_sequence_is_not_source_only(self):
        # This topology matches the earlier eight-node teaching graph. The
        # corrected rule lets newly burned nodes spread in the next round.
        graph, sources = parse_lines([
            "1 1 2:1 3:1 7:1",
            "2 0 1:1 4:1",
            "3 0 1:1",
            "4 2 2:1 5:1 8:1",
            "5 0 4:1 6:1",
            "6 3 5:1 8:1",
            "7 0 1:1",
            "8 0 4:1 6:1",
        ])
        history, first_burn = preview.simulate_rounds(graph, sources)
        self.assertEqual(history[0][2], [1])
        self.assertEqual(history[1][2], [2, 3, 4, 7])
        self.assertEqual(history[2][2], [5, 6, 8])
        self.assertEqual(set(first_burn.values()), {1, 2, 3})

    def test_saved_expected_file_matches_rounds(self):
        graph, sources = preview.load_input(
            ROOT / "datasets" / "graph-burning-path-9-two-round-scheduled"
        )
        history, first_burn = preview.simulate_rounds(graph, sources)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            preview.write_text_files(output, graph, sources, history, first_burn)
            expected = (output / "expected.tsv").read_text(encoding="utf-8")
            self.assertIn("2\tB\t1\n", expected)
            self.assertIn("4\tNB\t-1\n", expected)
            self.assertIn("8\tB\t2\n", expected)
            round_one = (output / "round-01-nodes.tsv").read_text(encoding="utf-8")
            self.assertIn("2\tB\t1\tyes\n", round_one)
            self.assertIn("8\tNB\t-1\tno\n", round_one)

    def test_prediction_matches_prior_saved_giraph_run(self):
        graph, sources = preview.load_input(
            ROOT / "datasets" / "graph-burning-path-9-scheduled"
        )
        _, first_burn = preview.simulate_rounds(graph, sources)
        predicted_rows = [
            "{}\tB\t{}".format(vertex, first_burn[vertex])
            for vertex in sorted(graph)
        ]
        saved_actual_rows = (
            ROOT / "results" / "graph-burning-path-9-scheduled" / "part-00000.txt"
        ).read_text(encoding="utf-8").splitlines()
        self.assertEqual(predicted_rows, saved_actual_rows)


if __name__ == "__main__":
    unittest.main()
