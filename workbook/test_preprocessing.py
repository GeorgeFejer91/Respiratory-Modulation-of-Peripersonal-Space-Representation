"""Independent reference checks for the preprocessing explainer."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import pandas as pd

from preparation import local_release_pair, load_pair

ROOT = Path(__file__).resolve().parents[1]


class PreprocessingTests(unittest.TestCase):
    def test_release_stages_match_independent_pandas(self):
        from preprocessing_data import build_payload
        people, trials = load_pair(*local_release_pair())
        payload = build_payload(people, trials)
        frame = pd.DataFrame(trials)
        frame["rt"] = pd.to_numeric(frame.reaction_time_ms, errors="coerce")
        frame["soa_ms"] = pd.to_numeric(frame.soa_ms, errors="coerce")
        catches = frame[frame.trial_type.eq("Catch")]
        bad = catches.groupby("participant_id").outcome.apply(lambda s: s.eq("false_alarm").mean() > .30)
        eligible = frame[~frame.participant_id.isin(bad[bad].index) &
                         frame.trial_type.isin(["Audio-Tactile", "Baseline"]) &
                         frame.outcome.eq("hit") & frame.response_given.eq("True") & frame.rt.notna()].copy()
        stats = eligible.groupby("participant_id").rt.agg(["mean", "std"])
        limits = eligible.join(stats, on="participant_id")
        trimmed = limits[limits.rt.between(limits["mean"] - 2.5*limits["std"],
                                          limits["mean"] + 2.5*limits["std"])]
        records = [dict(zip(payload["columns"], row)) for row in payload["rows"]]
        self.assertEqual({r["trial_id"] for r in records if r["eligible"]}, set(eligible.trial_id))
        self.assertEqual({r["trial_id"] for r in records if r["trimmed"]}, set(trimmed.trial_id))
        self.assertEqual(len(records), 17114)
        self.assertEqual(sum(r["rt"] is None for r in records), int(frame.rt.isna().sum()))
        module = (ROOT/"workbook/preprocessing_assets/engine.mjs").as_uri()
        script = f"""
import fs from 'node:fs'; import {{derive}} from {json.dumps(module)};
const data=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));
const out=[];
for(const cohort of ['primary40','full42']) for(const cutoff of ['none','200']) for(const normalization of ['z','range']) {{
const r=derive(data,{{cohort,cutoff,participant:'all',condition:'all',phase:'all',normalization}});
const filtered=derive(data,{{cohort,cutoff,participant:'P001',condition:'Control',phase:'Inhale',normalization}});
out.push({{cohort,cutoff,normalization,filtered:filtered[5].rows.map(r=>[r.trial_id,r.value]),
stages:r.map(s=>({{rows:s.rows.map(r=>[r.trial_id,r.value]),summary:s.summary}}))}});
}} console.log(JSON.stringify(out));"""
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"data.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            output = subprocess.run(["node", "--input-type=module", "-e", script, str(path)],
                                    check=True, capture_output=True, text=True)
        for case in json.loads(output.stdout):
            reference = trimmed.copy()
            if case["cohort"] == "primary40":
                reference = reference[~reference.participant_id.isin(["P011", "P033"])]
            if case["cutoff"] == "200":
                reference = reference[reference.rt.ge(200)]
            self.assertEqual({r[0] for r in case["stages"][3]["rows"]}, set(reference.trial_id))
            keys = ["participant_id", "condition", "phase"]
            baseline = reference[reference.trial_type.eq("Baseline")].groupby(keys).rt.mean()
            at = reference[reference.trial_type.eq("Audio-Tactile")].join(baseline.rename("baseline"), on=keys)
            at["corrected"] = at.rt - at.baseline
            expected = dict(zip(at.trial_id, at.corrected))
            for trial_id, value in case["stages"][4]["rows"]:
                if trial_id in expected:
                    self.assertAlmostEqual(value, expected[trial_id], places=9)
            norm = at.groupby("participant_id").corrected.transform
            at["z"] = ((at.corrected-norm("mean"))/norm("std") if case["normalization"] == "z"
                       else (at.corrected-norm("min"))/(norm("max")-norm("min")))
            expected_z = dict(zip(at.trial_id, at.z))
            for trial_id, value in case["stages"][5]["rows"]:
                if trial_id in expected_z:
                    self.assertAlmostEqual(value, expected_z[trial_id], places=9)
            for trial_id, value in case["filtered"]:
                if trial_id in expected_z:
                    self.assertAlmostEqual(value, expected_z[trial_id], places=9)
            means = at.groupby(keys+["soa_ms"]).corrected.mean().reset_index()
            expected_summary = means.groupby(["condition","phase","soa_ms"]).corrected.agg(["mean","std","count"])
            for row in case["stages"][4]["summary"]:
                expected_row = expected_summary.loc[(row["condition"], row["phase"], row["soa"])]
                self.assertAlmostEqual(row["mean"], expected_row["mean"], places=9)
                self.assertAlmostEqual(row["sd"], expected_row["std"], places=9)
                self.assertEqual(row["n"], expected_row["count"])

    def test_empty_and_constant_normalization_are_missing(self):
        module = (ROOT/"workbook/preprocessing_assets/engine.mjs").as_uri()
        script = f"""
import {{derive}} from {json.dumps(module)};
const columns=['trial_id','participant_id','condition','phase','trial_type','soa','rt','eligible','trimmed'];
const rows=[['a','P000','Control','Exhale','Audio-Tactile',300,0,true,true],
['b','P000','Control','Exhale','Audio-Tactile',800,0,true,true],
['c','P000','Control','Exhale','Baseline',300,0,true,true],
['d','P000','Control','Exhale','Audio-Tactile',1500,null,false,false]];
const data={{columns,rows}};
const a=derive(data,{{cohort:'primary40',cutoff:'none',participant:'all',condition:'all',phase:'all',normalization:'z'}});
const b=derive(data,{{cohort:'primary40',cutoff:'none',participant:'P999',condition:'all',phase:'all',normalization:'range'}});
console.log(JSON.stringify({{raw:a[0].summary,corrected:a[4].summary,normalized:a[5].summary,empty:b.map(s=>s.rows.length)}}));"""
        out = json.loads(subprocess.run(["node","--input-type=module","-e",script], check=True,
                                       capture_output=True,text=True).stdout)
        self.assertEqual(len(out["raw"]), 2)
        self.assertEqual(out["corrected"][0]["mean"], 0)
        self.assertIsNone(out["corrected"][0]["sd"])
        self.assertEqual(out["normalized"], [])
        self.assertEqual(out["empty"], [0]*6)


if __name__ == "__main__":
    unittest.main()
