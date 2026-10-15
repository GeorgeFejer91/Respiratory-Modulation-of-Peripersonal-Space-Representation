"""Install the owner's reviewed, pinned research and coding skills; preserve existing copies."""

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


SOURCES = [
    ("multi-source-web-search", "GeorgeFejer91/multi-source-web-search",
     "7f3e70744d1fffbf7c59e084d48384bae09c1e6f", "multi-source-web-search"),
    ("ponytail", "DietrichGebert/ponytail",
     "84740e3d344b69b4a133201fa519eb37a62a2b2a", "skills/ponytail"),
]


def install(root):
    root.mkdir(parents=True, exist_ok=True)
    for name, repository, commit, subdirectory in SOURCES:
        destination = root / name
        if destination.exists():
            if not (destination / "SKILL.md").is_file():
                raise RuntimeError(f"Existing incomplete skill needs review: {destination}")
            print(f"Preserved existing {name}")
            continue
        with tempfile.TemporaryDirectory(prefix="study5-skill-") as directory:
            subprocess.run(["git", "clone", "--quiet", "--no-checkout", "--filter=blob:none",
                            f"https://github.com/{repository}.git", directory], check=True)
            subprocess.run(["git", "-C", directory, "checkout", "--quiet", "--detach", commit], check=True)
            source = Path(directory) / subdirectory
            if not (source / "SKILL.md").is_file() or any(p.is_symlink() for p in source.rglob("*")):
                raise RuntimeError("Missing skill or unexpected symlink in pinned source")
            shutil.copytree(source, destination)
        print(f"Installed {name} from {repository}@{commit}; skill files only")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.home() / ".codex/skills")
    install(parser.parse_args().root)
