"""Build only the synthetic/upload workbook, never the repository's raw data."""

import argparse
import subprocess
import sys
from pathlib import Path


def build(output):
    notebook = Path(__file__).resolve().with_name("data_preparation.py")
    for mode, target in (("run", output), ("edit", output / "editor")):
        subprocess.run([
            sys.executable, "-m", "marimo", "export", "html-wasm", str(notebook),
            "--output", str(target), "--mode", mode, "--no-sandbox", "--no-execute", "--force",
        ], check=True)
    (output / ".nojekyll").touch()
    # Prevent a future exporter/configuration change from silently copying raw inputs.
    if list(output.rglob("*.csv")):
        raise RuntimeError("Unexpected CSV data in the public site artifact.")
    for target in (output, output / "editor"):
        if not (target / "index.html").is_file():
            raise RuntimeError("Missing workbook HTML.")
    print(f"Built reactive application and editable workbook in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(".for-ai-local/site"))
    build(parser.parse_args().output.resolve())
