"""Behavioral checks for data preparation and the browser publication boundary."""

import copy
import csv
import io
import json
import unittest
import zipfile
from hashlib import sha256
from pathlib import Path

from preparation import (
    FILES, PARTICIPANT_COLUMNS, TRIAL_COLUMNS, demo_pair, encode_csv,
    load_pair, make_bundle, prepare,
)


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.sources = demo_pair()
        self.people, self.trials = load_pair(*self.sources)
        self.settings = {
            "trial_types": ["Audio-Tactile", "Baseline"],
            "conditions": ["Control", "Viscereality"],
            "phases": ["Inhale", "Exhale"], "window": "No RT window",
        }

    def test_demo_contains_only_generated_observations(self):
        self.assertEqual((len(self.people), len(self.trials)), (8, 480))
        self.assertTrue(all(p["data_availability"] == "synthetic" for p in self.people))
        self.assertEqual(self.sources, demo_pair())

    def test_preparation_is_a_view_with_a_conserved_sequential_audit(self):
        before = copy.deepcopy((self.people, self.trials))
        prepared, stages, columns = prepare(self.people, self.trials, **self.settings)
        self.assertEqual(len(prepared), 376)
        self.assertEqual(sum(s["rows_removed_here"] for s in stages) + len(prepared), 480)
        self.assertTrue(all(r["trial_type"] != "Catch" and r["outcome"] == "hit" for r in prepared))
        self.assertEqual(prepared[0]["participant_age_years"], "22")
        self.assertIn("participant_condition_order", columns)
        self.assertEqual((self.people, self.trials), before)

    def test_windows_use_recorded_flags_and_preserve_their_order(self):
        counts = []
        for label in ("No RT window", "Recorded 100–2000 ms flag", "Recorded 200–2000 ms flag"):
            rows, _, _ = prepare(self.people, self.trials, **(self.settings | {"window": label}))
            counts.append(len(rows))
            if label != "No RT window":
                flag = "rt_valid_100_2000" if "100" in label else "rt_valid_200_2000"
                self.assertTrue(all(r[flag] == "True" for r in rows))
        self.assertGreater(counts[0], counts[1])
        self.assertGreater(counts[1], counts[2])

    def test_empty_selection_exports_headers_and_a_zero_row_manifest(self):
        settings = self.settings | {"conditions": []}
        prepared, stages, columns = prepare(self.people, self.trials, **settings)
        bundle, manifest = make_bundle(prepared, columns, stages, sources=self.sources, settings=settings, synthetic=True)
        self.assertEqual(prepared, [])
        self.assertEqual(stages[-1]["rows_retained"], 0)
        with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
            self.assertEqual(len(archive.read("prepared_trials.csv").decode().splitlines()), 1)
        self.assertTrue(manifest["synthetic_demo"])

    def test_download_records_exact_sources_choices_and_output(self):
        prepared, stages, columns = prepare(self.people, self.trials, **self.settings)
        args = dict(sources=self.sources, settings=self.settings, synthetic=True)
        bundle, manifest = make_bundle(prepared, columns, stages, **args)
        self.assertEqual(bundle, make_bundle(prepared, columns, stages, **args)[0])
        with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
            self.assertEqual(set(archive.namelist()), {"prepared_trials.csv", "preparation_manifest.json"})
            output = archive.read("prepared_trials.csv")
            self.assertEqual(len(list(csv.DictReader(io.StringIO(output.decode())))), len(prepared))
            self.assertEqual(json.loads(archive.read("preparation_manifest.json")), manifest)
            self.assertEqual(sha256(output).hexdigest(), manifest["prepared_csv_sha256"])
        self.assertEqual(manifest["source_sha256"][FILES[0]], sha256(self.sources[0]).hexdigest())
        self.assertEqual(manifest["settings"], self.settings)

    def test_invalid_inputs_are_rejected_before_preparation(self):
        for field, value in (("participant_id", "P999"), ("trial_id", "duplicate"),
                             ("noise_type", "C:\\Users\\private"),
                             ("reaction_time_ms", "NaN"), ("rt_valid_100_2000", "1")):
            with self.subTest(field=field):
                trials = copy.deepcopy(self.trials)
                trials[0][field] = value
                with self.assertRaises(ValueError):
                    load_pair(self.sources[0], encode_csv(TRIAL_COLUMNS, trials))
        with self.assertRaisesRegex(ValueError, "columns"):
            load_pair(b"wrong\nvalue\n", self.sources[1])
        with self.assertRaisesRegex(ValueError, "malformed"):
            load_pair(self.sources[0], (",".join(TRIAL_COLUMNS) + "\nP000\n").encode())

    def test_current_repository_data_pass_without_becoming_demo_inputs(self):
        root = Path(__file__).resolve().parents[1]
        real_sources = tuple((root / "data/raw" / name).read_bytes() for name in FILES)
        people, trials = load_pair(*real_sources)
        self.assertEqual((len(people), len(trials)), (42, 17114))
        self.assertTrue(all(a != b for a, b in zip(real_sources, self.sources)))


if __name__ == "__main__":
    unittest.main()
