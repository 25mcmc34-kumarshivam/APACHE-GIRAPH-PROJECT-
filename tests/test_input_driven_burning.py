"""Local tests for the schedule parser and readable-result formatter."""

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


schedule = load_script("validate_burning_schedule.py")
formatter = load_script("format_burning_output.py")


class InputDrivenBurningTests(unittest.TestCase):
    def path_lines(self):
        folder = ROOT / "datasets" / "graph-burning-path-9-scheduled"
        for file in sorted(folder.glob("*.txt")):
            yield from file.read_text(encoding="utf-8").splitlines()

    def test_path_schedule_and_first_burn_rounds(self):
        graph, sources = schedule.parse_lines(self.path_lines())
        self.assertEqual(len(graph), 9)
        self.assertEqual(sources, {1: 3, 2: 8, 3: 6})
        self.assertEqual(
            schedule.predicted_rounds(graph, sources),
            {1: 3, 2: 2, 3: 1, 4: 2, 5: 3, 6: 3, 7: 3, 8: 2, 9: 3},
        )

    def test_unburned_vertices_use_minus_one(self):
        lines = [line.split() for line in self.path_lines()]
        for fields in lines:
            fields[1] = "1" if fields[0] == "2" else "2" if fields[0] == "8" else "0"
        graph, sources = schedule.parse_lines(" ".join(fields) for fields in lines)
        result = schedule.predicted_rounds(graph, sources)
        self.assertEqual([vertex for vertex in sorted(result) if result[vertex] == -1],
                         [4, 5, 6, 7, 9])

    def test_committed_two_round_dataset(self):
        folder = ROOT / "datasets" / "graph-burning-path-9-two-round-scheduled"
        lines = (
            line
            for file in sorted(folder.glob("*.txt"))
            for line in file.read_text(encoding="utf-8").splitlines()
        )
        graph, sources = schedule.parse_lines(lines)
        self.assertEqual(sources, {1: 2, 2: 8})
        self.assertEqual(
            schedule.predicted_rounds(graph, sources),
            {1: 2, 2: 1, 3: 2, 4: -1, 5: -1, 6: -1, 7: -1, 8: 2, 9: -1},
        )

    def test_reject_two_sources_in_one_round(self):
        with self.assertRaisesRegex(ValueError, "choose one source per round"):
            schedule.parse_lines(["1 1 2:1", "2 1 1:1"])

    def test_reject_missing_round(self):
        with self.assertRaisesRegex(ValueError, "no source is selected in round 2"):
            schedule.parse_lines(["1 1 2:1", "2 3 1:1"])

    def test_reject_source_burned_earlier(self):
        with self.assertRaisesRegex(ValueError, "already burned before round 3"):
            schedule.parse_lines([
                "1 1 2:1", "2 3 1:1 3:1", "3 2 2:1"
            ])

    def test_reject_missing_reverse_edge(self):
        with self.assertRaisesRegex(ValueError, "lacks a reverse edge"):
            schedule.parse_lines(["1 1 2:1", "2 0"])

    def test_reject_duplicate_vertex_id(self):
        with self.assertRaisesRegex(ValueError, "defined twice"):
            schedule.parse_lines(["1 1", "1 0"])

    def test_format_burned_and_unburned(self):
        self.assertEqual(formatter.format_line("17\t5.0\n"), "17\tB\t5")
        self.assertEqual(formatter.format_line("5\t0.0\n"), "5\tNB\t-1")
        self.assertEqual(formatter.format_line("6\t-3.0\n"), "6\tNB\t-1")

    def test_reject_noninteger_burn_round(self):
        with self.assertRaisesRegex(ValueError, "non-integer"):
            formatter.format_line("4\t2.5")


if __name__ == "__main__":
    unittest.main()
