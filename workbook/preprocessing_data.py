"""Publish a compact, audited view of the existing cleaner, without refitting."""
import json
import math
from collections import defaultdict
from hashlib import sha256
from html import escape
from statistics import mean, stdev

from paper_analysis import clean, numeric
from preparation import FILES

COLUMNS = ["trial_id", "participant_id", "condition", "phase", "trial_type",
           "soa", "rt", "eligible", "trimmed"]


def build_payload(people, trials):
    retained, quality, counts = clean(people, trials)
    kept = {r["trial_id"] for r in retained}
    excluded = {r["participant_id"] for r in quality if r["excluded_catch"]}
    rows = []
    for r in trials:
        rt, soa = numeric(r, "reaction_time_ms"), numeric(r, "soa_ms")
        eligible = (r["participant_id"] not in excluded and
                    r["trial_type"] in ("Audio-Tactile", "Baseline") and
                    r["outcome"] == "hit" and r["response_given"] == "True" and math.isfinite(rt))
        rows.append([r["trial_id"], r["participant_id"], r["condition"], r["phase"],
                     r["trial_type"], soa if math.isfinite(soa) else None,
                     rt if math.isfinite(rt) else None, eligible, r["trial_id"] in kept])
    return dict(schema_version=1, columns=COLUMNS, rows=rows, quality=quality, audit=counts)


def build_preprocessing(root, destination, people, trials, sources):
    destination.mkdir(parents=True, exist_ok=True)
    payload = build_payload(people, trials)
    payload["provenance"] = {
        "status": "descriptive preprocessing comparison; no model fitting",
        "input_sha256": {name: sha256(content).hexdigest() for name, content in zip(FILES, sources)},
        "code_sha256": {name: sha256((root/name).read_bytes()).hexdigest() for name in
                        ("workbook/paper_analysis.py", "workbook/preprocessing_data.py",
                         "workbook/preprocessing_assets/engine.mjs", "workbook/preprocessing_assets/app.js",
                         "workbook/preprocessing_assets/index.html", "workbook/preprocessing_assets/style.css")},
        "cleaning": "Eligible AT/Baseline hits; participant mean ± 2.5 sample SD; optional RT ≥200 ms afterward.",
        "baseline": "Retained participant × Condition × Phase baseline mean; AT minus Baseline.",
        "normalization": "Each person's retained corrected AT trials, all conditions/phases/SOAs, before view filters.",
    }
    (destination/"data.json").write_text(json.dumps(payload, allow_nan=False, separators=(",", ":")), encoding="utf-8")
    # A readable, complete default comparison remains available without JavaScript.
    records = [dict(zip(COLUMNS, row)) for row in payload["rows"]
               if row[1] not in ("P011", "P033")]
    summaries = []
    for flag in ("eligible", "trimmed"):
        cells = defaultdict(list)
        for row in records:
            if row[flag] and row["trial_type"] == "Audio-Tactile":
                cells[(row["participant_id"], row["condition"], row["phase"], row["soa"])].append(row["rt"])
        grouped = defaultdict(list)
        for (_, condition, phase, soa), values in cells.items():
            grouped[(condition, phase, soa)].append(mean(values))
        summaries.append({key: (mean(values), stdev(values) if len(values)>1 else None, len(values))
                          for key, values in grouped.items()})
    rows = []
    for key in sorted(set(summaries[0]) | set(summaries[1])):
        cells = ['<th scope="row">'+escape(f"{key[0]} · {key[1]} · {key[2]:g} ms")+'</th>']
        for label, summary in zip(("Before", "After"), summaries):
            values = summary.get(key, (None, None, 0))
            cells.append(f'<td data-label="{label}">'+escape(" · ".join("Missing" if v is None else str(v) for v in values))+'</td>')
        rows.append('<tr>'+''.join(cells)+'</tr>')
    before_count = sum(r["eligible"] and r["trial_type"] == "Audio-Tactile" for r in records)
    after_count = sum(r["trimmed"] and r["trial_type"] == "Audio-Tactile" for r in records)
    (destination/"default-summary.html").write_text('''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Static preprocessing comparison · Study 5</title><link rel="stylesheet" href="style.css">
<header><nav><a href="./">Interactive preprocessing</a><a href="../">Living paper</a></nav></header>
<main><h1>The default comparison</h1><p>Primary cohort (40 records), all conditions and phases.
Before: eligible responses. After: the single participant ±2.5 sample-SD filter, with no minimum-RT cutoff.
These descriptive summaries are generated directly from the released data and canonical cleaner.</p>
<p>Audio–tactile trial values: '''+f'{before_count:,} before; {after_count:,} after; {before_count-after_count:,} removed.'+'''</p>
<p>Each cell averages trials within participant, then averages participants equally.
Mean and sample SD are in milliseconds; n counts participants. SD is not a confidence interval.
Full precision is retained below. Missing values remain missing.</p>
<table id="summary"><caption>Complete participant-weighted SOA summaries</caption><thead><tr>
<th scope="col">Condition / phase / SOA</th><th scope="col">Before: mean · SD · n</th><th scope="col">After: mean · SD · n</th>
</tr></thead><tbody>'''+''.join(rows)+'''</tbody></table>
<p><a href="data.json" download>Download the audited input and source hashes</a></p></main></html>''',encoding="utf-8")
