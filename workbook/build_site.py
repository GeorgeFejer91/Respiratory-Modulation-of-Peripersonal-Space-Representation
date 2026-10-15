"""Build the publication companion and its audited deidentified data release."""

import argparse
import subprocess
import sys
import shutil
import json
import zipfile
import io
from hashlib import sha256
from pathlib import Path

from preparation import FILES,load_pair,audit_release


def build(output):
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
        for name in ("ANALYSIS_PLAN.md","DATA_RELEASE.md"):
            shutil.copyfile(notebook.parent/name,target/name)
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
        for name,expected_hash in manifest["code_sha256"].items():
            if sha256((notebook.parent/name).read_bytes()).hexdigest()!=expected_hash:
                raise RuntimeError("Engine changed: rerun the browser analysis and refresh its reference record.")
        (target/"paper.pdf").write_bytes(pdf)
    (output / ".nojekyll").touch()
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
    build(parser.parse_args().output.resolve())
