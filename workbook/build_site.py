"""Build the publication companion and its audited deidentified data release."""

import argparse
import subprocess
import sys
import shutil
import json
import zipfile
import io
import re
from hashlib import sha256
from pathlib import Path
from html import escape

import markdown

from preparation import FILES,load_pair,audit_release


def build_review(root, target):
    """Render the reviewed Markdown using marimo's existing Markdown dependency."""
    source = root / "literature_review"
    destination = target / "literature_review"
    destination.mkdir(exist_ok=True)
    pages = {"README.md": "index.html", "EVIDENCE_TABLE.md": "EVIDENCE_TABLE.html",
             "ANALYSIS_RATIONALE.md": "ANALYSIS_RATIONALE.html", "SEARCH_LOG.md": "SEARCH_LOG.html",
             "QUESTIONNAIRES.md": "QUESTIONNAIRES.html", "INDIVIDUAL_PARAMETERS.md":"INDIVIDUAL_PARAMETERS.html"}
    links = dict(pages)
    links.update({"../analysis/sigmoid_literature_sources.json": "../sigmoid_literature_sources.json",
                  "../analysis/questionnaire_literature_sources.json": "../questionnaire_literature_sources.json",
                  "../analysis/participant_literature_sources.json": "../participant_literature_sources.json",
                  "../results/browser-analysis/analysis_report.md": "../reference/analysis_report.md"})
    for name in ("ANALYSIS_PLAN.md", "SIGMOID_EXPLORATION.md"):
        links["../workbook/" + name] = "../" + name
    code = destination / "analysis_source"
    code.mkdir(exist_ok=True)
    for name in ("paper_analysis.py", "descriptive_sigmoid.py", "sigmoid_shape.py", "publication_report.py", "questionnaires.py", "participant_sigmoid.py", "participant_report.py"):
        shutil.copyfile(root / "workbook" / name, code / name)
        links["../workbook/" + name] = "analysis_source/" + name
    for name in (*pages, "searches.json", "references.bib"):
        shutil.copyfile(source / name, destination / name)
    for name, output_name in pages.items():
        text = (source / name).read_text()
        body = markdown.markdown(text, extensions=["tables", "fenced_code"])
        for old, new in links.items():
            body = body.replace('href="' + old + '"', 'href="' + new + '"')
        title = escape(text.splitlines()[0].lstrip("# "))
        (destination / output_name).write_text(f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Study 5</title><style>
body{{font:17px/1.65 system-ui,sans-serif;color:#1f2937;margin:2rem auto;padding:0 1.2rem;max-width:1050px}}
a{{color:#175b9e}}h1,h2{{line-height:1.25}}h2{{margin-top:2.2rem}}p,li{{max-width:82ch}}
table{{display:block;overflow-x:auto;border-collapse:collapse;font-size:14px;line-height:1.5}}
th,td{{padding:.65rem;text-align:left;vertical-align:top;border:1px solid #ccd5df;min-width:170px}}
th{{background:#edf3f8}}code{{background:#f0f3f6;overflow-wrap:anywhere}}blockquote{{border-left:3px solid #8aaac6;padding-left:1rem}}
nav{{font-size:15px;margin-bottom:2rem}}:focus-visible{{outline:3px solid #c75c12}}
</style><nav><a href="../">Workbook</a> · <a href="index.html">Review</a> ·
<a href="EVIDENCE_TABLE.html">Evidence</a> · <a href="ANALYSIS_RATIONALE.html">Rationale</a> ·
<a href="QUESTIONNAIRES.html">Questionnaires</a> · <a href="INDIVIDUAL_PARAMETERS.html">Individual curves</a> · <a href="SEARCH_LOG.html">Search record</a> · <a href="{name}">Markdown source</a></nav>
<main>{body}</main></html>''')


def build_results(root, target):
    """Publish the independently verified results branch without refreshing the paper."""
    from validate_bayesian import verified_bundle
    source = root/"results"/"bayesian"
    _, manifest, digest = verified_bundle(source/"bayesian-results.zip")
    for name, expected in manifest["artifact_sha256"].items():
        if "/" not in name and sha256((source/name).read_bytes()).hexdigest() != expected:
            raise RuntimeError("Promoted Bayesian artifact differs from the browser download: "+name)
    data = (source/"bayesian-results.zip").read_bytes()
    destination = target/"results"
    destination.mkdir(exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if manifest["runtime"]["execution"] != "browser Pyodide" or manifest["manuscript_updated"]:
            raise RuntimeError("An actual results-only browser download is required.")
        for name in ("bayesian_results.json", "bayesian_results.md", "bayesian_average_curves.svg", "bayesian_cell_parameters.svg",
                     "bayesian_parameter_contrasts.svg", "bayesian_participant_atlas.pdf"):
            (destination/name).write_bytes(archive.read(name))
    (destination/"bayesian-results.zip").write_bytes(data)
    report = (root/"results"/"RESULTS_REPORT.md").read_text()
    (destination/"RESULTS_REPORT.md").write_text(report)
    evidence = (root/"results"/"bayesian-independent-validation.json").read_bytes()
    (destination/"bayesian-independent-validation.json").write_bytes(evidence)
    checked = json.loads(evidence)
    if checked.get("browser_zip_sha256") != digest:
        raise RuntimeError("Bayesian browser validation/reference mismatch.")
    if checked.get("browser_ui", {}).get("source_sha256") != sha256((root/"workbook"/"data_preparation.py").read_bytes()).hexdigest():
        raise RuntimeError("Workbook UI changed after its browser check.")
    for filename, text in (("index.html", report), ("bayesian_results.html", (destination/"bayesian_results.md").read_text())):
        body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
        # Repository-relative evidence links resolve to shipped assets or their exact public source.
        def rewrite(match):
            attribute, path = match.groups()
            if path.startswith(("https://", "http://", "#")):
                return match.group(0)
            local = path.removeprefix("bayesian/")
            if (destination/local).is_file():
                path = local
            elif path == "../for-ai/ANALYSIS_ROADMAP.md":
                path = "https://github.com/GeorgeFejer91/Study5_Publication/blob/main/for-ai/ANALYSIS_ROADMAP.md"
            elif path == "../workbook/ANALYSIS_PLAN.md":
                path = "../ANALYSIS_PLAN.md"
            elif path == "browser-analysis/analysis_report.md":
                path = "../reference/analysis_report.md"
            elif path == "browser-analysis/browser-results.zip":
                path = "../reference/browser-results.zip"
            else:
                relative = (Path("results")/path).as_posix()
                path = "https://github.com/GeorgeFejer91/Study5_Publication/blob/main/"+relative
            return attribute+'="'+path+'"'
        body = re.sub(r'(href|src)="([^"\s]+)"', rewrite, body)
        (destination/filename).write_text('''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Study 5 · Results</title>
<style>body{font:17px/1.65 system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1.2rem;color:#1f2937}
a{color:#175b9e}h1,h2{line-height:1.25}h2{margin-top:2.2rem}img{max-width:100%;height:auto}
table{display:block;overflow-x:auto;border-collapse:collapse;font-size:14px}th,td{padding:.6rem;border:1px solid #ccd5df;text-align:left;vertical-align:top}
th{background:#edf3f8}code{overflow-wrap:anywhere}nav{font-size:15px}:focus-visible{outline:3px solid #c75c12}</style>
<nav><a href="../">Workbook</a> · <a href="../pivot/">Pivot explorer</a> · <a href="index.html">Results report</a> ·
<a href="bayesian_results.html">Bayesian detail</a> · <a href="https://github.com/GeorgeFejer91/Study5_Publication/blob/main/for-ai/ANALYSIS_ROADMAP.md">Question checklist</a> ·
<a href="bayesian-results.zip">Download results</a> · <a href="bayesian_participant_atlas.pdf">Individual curves</a></nav>
<main>'''+body+"</main></html>")
    (destination/"results_manifest.json").write_text(json.dumps(dict(
        browser_zip_sha256=sha256(data).hexdigest(), results_report_sha256=sha256(report.encode()).hexdigest(),
        manuscript_updated=False), indent=2)+"\n")


def build(output, development=False):
    notebook = Path(__file__).resolve().with_name("data_preparation.py")
    root=notebook.parent.parent
    sources=tuple((root/"data"/"raw"/name).read_bytes() for name in FILES)
    people,trials=load_pair(*sources)
    audit_release(people,trials)
    if len(people)!=42 or len(trials)!=17114:
        raise RuntimeError("Release cohort changed: repeat the field audit and backup first.")
    expected={
        "study5_participants.csv":"5f4aac1802f86ec8945a2676c47299b18c5e1e5bb2fdd0edb9cbdcbd79022b6d",
        "study5_pps_trials.csv":"45e53d49c436474df7c9674b54fb796e3fd95ed641a6b71e807ff3ca32e25d1d",
    }
    if any(sha256(data).hexdigest()!=expected[name] for name,data in zip(FILES,sources)):
        raise RuntimeError("Release hashes changed: repeat the audit and backup before publishing.")
    allowed=[]
    for mode, target in (("run", output), ("edit", output / "editor")):
        subprocess.run([
            sys.executable, "-m", "marimo", "export", "html-wasm", str(notebook),
            "--output", str(target), "--mode", mode, "--no-sandbox", "--no-execute", "--force",
        ], check=True)
        data_dir=target/"public"/"data"
        data_dir.mkdir(parents=True,exist_ok=True)
        for name,data in zip(FILES,sources):
            path=data_dir/name
            path.write_bytes(data)
            if sha256(path.read_bytes()).hexdigest()!=expected[name]:
                raise RuntimeError("Published CSV hash mismatch.")
            allowed.append(path.resolve())
        (data_dir/"sha256.json").write_text(json.dumps(expected,indent=2)+"\n")
        for name in ("ANALYSIS_PLAN.md","DATA_RELEASE.md","SIGMOID_EXPLORATION.md"):
            document = (notebook.parent/name).read_text().replace(
                "../literature_review/README.md", "./literature_review/index.html").replace(
                "../literature_review/QUESTIONNAIRES.md", "./literature_review/QUESTIONNAIRES.html")
            (target/name).write_text(document)
        shutil.copyfile(root/"analysis/sigmoid_literature_sources.json",target/"sigmoid_literature_sources.json")
        shutil.copyfile(root/"analysis/questionnaire_literature_sources.json",target/"questionnaire_literature_sources.json")
        shutil.copyfile(root/"analysis/participant_literature_sources.json",target/"participant_literature_sources.json")
        build_review(root, target)
        if development:
            # Run the changed engine in a real browser before a new reference/PDF exists.
            # Never copy stale publication records into this development artifact.
            for stale in (target/"paper.pdf",target/"reference"):
                if stale.is_dir():shutil.rmtree(stale)
                elif stale.exists():stale.unlink()
            continue
        reference=target/"reference"
        reference.mkdir(exist_ok=True)
        for name in ("analysis_report.md","browser-results.zip"):
            shutil.copyfile(root/"results"/"browser-analysis"/name,reference/name)
        preprint=json.loads((root/"results"/"preprint_manifest.json").read_text())
        for name,expected_hash in preprint["manuscript_sha256"].items():
            if sha256((root/name).read_bytes()).hexdigest()!=expected_hash:
                raise RuntimeError("Preprint sources changed: rebuild and review the PDF first.")
        pdf=(root/"results"/"study5-preprint.pdf").read_bytes()
        if sha256(pdf).hexdigest()!=preprint["pdf_sha256"]:
            raise RuntimeError("Preprint PDF hash mismatch.")
        browser_zip=(reference/"browser-results.zip").read_bytes()
        if sha256(browser_zip).hexdigest()!=preprint["browser_zip_sha256"]:
            raise RuntimeError("Preprint/reference browser run mismatch.")
        with zipfile.ZipFile(io.BytesIO(browser_zip)) as archive:
            manifest=json.loads(archive.read("manifest.json"))
            atlas=archive.read("participant_curve_atlas.pdf")
            if sha256(atlas).hexdigest()!=manifest["artifact_sha256"]["participant_curve_atlas.pdf"]:
                raise RuntimeError("Individual curve atlas hash mismatch.")
            (target/"individual-curves.pdf").write_bytes(atlas)
        for name,expected_hash in manifest["code_sha256"].items():
            if sha256((notebook.parent/name).read_bytes()).hexdigest()!=expected_hash:
                raise RuntimeError("Engine changed: rerun the browser analysis and refresh its reference record.")
        (target/"paper.pdf").write_bytes(pdf)
        build_results(root, target)
    from pivot_data import build_snapshots
    pivot = output / "pivot"
    shutil.copytree(notebook.parent / "pivot_assets", pivot, dirs_exist_ok=True)
    subprocess.run([
        sys.executable, "-m", "marimo", "export", "html-wasm", str(notebook.with_name("pivot_explorer.py")),
        "--output", str(pivot / "app"), "--mode", "run", "--no-sandbox", "--no-execute", "--force",
    ], check=True)
    catalog = build_snapshots(root, pivot / "app" / "public" / "snapshots")
    if not catalog:
        raise RuntimeError("Missing saved-result pivot catalogue.")
    for target, href, script in ((output, "pivot/", "pivot/text-fit.js"),
                                 (output / "editor", "../pivot/", "../pivot/text-fit.js")):
        page = target / "index.html"
        navigation = f'''<header style="font:16px/24px Arial,sans-serif;padding:8px 16px;border-bottom:1px solid #ccd5df;box-sizing:border-box">
<nav aria-label="Study 5 exploration"><a data-measure style="display:block;max-width:100%;color:#175b9e;overflow-wrap:break-word" href="{href}">Open the interactive pivot explorer</a></nav></header>
<script type="module" src="{script}"></script>'''
        page.write_text(re.sub(r"(<body[^>]*>)", lambda match: match.group(0) + navigation,
                               page.read_text(encoding="utf-8"), count=1), encoding="utf-8")
    (output / ".nojekyll").touch()
    marker=output/"DEVELOPMENT_ONLY.txt"
    if development:
        marker.write_text("Unpublished browser verification build. No reference report or paper.\n")
    elif marker.exists():
        marker.unlink()
    if set(p.resolve() for p in output.rglob("*.csv"))!=set(allowed):
        raise RuntimeError("Unexpected CSV in the publication artifact.")
    if list(output.rglob("__marimo__")) or list(output.rglob("private-backups")):
        raise RuntimeError("Private backup or execution cache in public artifact.")
    for target in (output, output / "editor"):
        if not (target / "index.html").is_file():
            raise RuntimeError("Missing workbook HTML.")
    print(f"Built reactive application and editable workbook in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(".for-ai-local/site"))
    parser.add_argument("--development",action="store_true",help="Unpublished verification build without a reference report or PDF; release checks remain mandatory by default.")
    args=parser.parse_args()
    build(args.output.resolve(),development=args.development)
