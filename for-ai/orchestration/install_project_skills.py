"""Install missing project-routed skills from reviewed, pinned local checkouts.

Download checkouts into the owner's canonical GitHub folder first. This copies
skill assets only; it never runs upstream installers, hooks, examples or packages.
"""

import ast
import importlib.util
import json
import re
import subprocess
from hashlib import sha256
from pathlib import Path

import yaml


def install():
    home = Path.home()
    github = home / "Documents/GitHub"
    destination = home / ".codex/skills"
    project = Path(__file__).resolve().parents[2]
    helper_path = destination / ".system/skill-installer/scripts/install-skill-from-github.py"
    import sys
    sys.path.insert(0, str(helper_path.parent))
    spec = importlib.util.spec_from_file_location("skill_installer", helper_path)
    helper = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helper
    spec.loader.exec_module(helper)
    validator_path = destination / ".system/skill-creator/scripts/quick_validate.py"
    validator_spec = importlib.util.spec_from_file_location("skill_validator", validator_path)
    validator = importlib.util.module_from_spec(validator_spec)
    validator_spec.loader.exec_module(validator)

    entries = []
    for manifest in ("visualization_skills.json", "spreadsheet_skills.json"):
        entries.extend(json.loads((project / "for-ai/orchestration" / manifest).read_text())["skills"])
    entries.extend([
        dict(name="statistical-analysis", repository="K-Dense-AI/scientific-agent-skills",
             commit="593377bb048752abb0152deab9fbb1083a6087df", subdirectory="skills/statistical-analysis"),
        *[dict(name=name, repository="soupandpsy/amazing-psycoder-skills",
               commit="3b9a0ac8763e85f1f36beef3d73f9ffb5d26172b", subdirectory="amazing-psycoder/" + name)
          for name in ("psy-ana-coder", "psy-ana-reviewer")],
    ])
    composition = json.loads((destination / "for-ai/references/toolkit-provenance.json").read_text())
    for name in composition["superpowers"]["skills"]:
        entries.append(dict(name=name, repository="obra/superpowers",
                            commit=composition["superpowers"]["revision"],
                            subdirectory="skills/" + name.removeprefix("superpowers-")))
    for name in composition["gsd_core"]["skills"]:
        entries.append(dict(name=name, repository="open-gsd/gsd-core",
                            commit=composition["gsd_core"]["revision"], subdirectory="skills/" + name))
    for name in ("agents-inc-accessibility", "agents-inc-web-performance", "mobx-integration"):
        entries.append(dict(name=name, local_source=destination / "for-ai/skills" / name))
    for name in ("rtk", "gsd-core-workflow", "superpowers-workflow"):
        entries.append(dict(name=name, local_source=project / "for-ai/skills" / name))

    receipts = []
    for entry in entries:
        name = entry["name"]
        target = destination / name
        if target.exists() and (target / "INSTALLATION.json").is_file():
            if not (target / "SKILL.md").is_file():
                raise RuntimeError("Incomplete existing skill: " + name)
            ok, reason = validator.validate_skill(target)
            if not ok:
                raise RuntimeError(name + ": " + reason)
            receipts.append(json.loads((target / "INSTALLATION.json").read_text(encoding="utf-8")))
            print("Preserved " + name)
            continue
        if "local_source" in entry:
            source = entry["local_source"]
            root = source
        else:
            root = github / entry["repository"].split("/")[-1]
            revision = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            if revision != entry["commit"]:
                raise RuntimeError("Source revision mismatch: " + name)
            source = root / entry["subdirectory"]
        helper._validate_skill(str(source), str(root))
        for script in source.rglob("*.py"):
            ast.parse(script.read_text(encoding="utf-8-sig"), filename=str(script))
        if not target.exists():
            helper._copy_skill(str(source), str(target))
        adaptations = []
        # Keep upstream metadata while satisfying Codex's installed validator.
        skill = target / "SKILL.md"
        text = skill.read_text(encoding="utf-8-sig")
        match = re.match(r"---\n(.*?)\n---", text, re.S)
        header = match[1]
        if name == "univer-integrate":
            header = re.sub(r"^description: (.+)$", lambda m: "description: " + json.dumps(m[1]), header, flags=re.M)
            adaptations.append("Quoted upstream colon-containing YAML description.")
        metadata = yaml.safe_load(header)
        metadata["name"] = name
        allowed = {"name", "description", "license", "allowed-tools", "metadata"}
        extra = {key: metadata.pop(key) for key in list(metadata) if key not in allowed}
        if extra:
            metadata.setdefault("metadata", {}).update(extra)
            adaptations.append("Preserved extra upstream frontmatter inside metadata.")
        if len(metadata["description"]) > 1024 or any(c in metadata["description"] for c in "<>"):
            metadata.setdefault("metadata", {})["upstream-description"] = metadata["description"]
            metadata["description"] = re.sub(r"[<>]", "", metadata["description"])[:1000].rsplit(" ", 1)[0]
            adaptations.append("Shortened discovery description; full original retained in metadata.")
        text = "---\n" + yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True) + "---" + text[match.end():]
        skill.write_text(text, encoding="utf-8")
        if name.startswith("superpowers-") and "repository" in entry:
            roster = [p.name for p in (root / "skills").iterdir() if p.is_dir()]
            for path in target.rglob("*.md"):
                content = path.read_text(encoding="utf-8")
                content = re.sub(r"superpowers:([a-z-]+)", r"superpowers-\1", content)
                for sibling in roster:
                    content = content.replace("../" + sibling + "/", "../superpowers-" + sibling + "/")
                path.write_text(content, encoding="utf-8")
            adaptations.append("Prefixed skill identifiers and sibling references with superpowers-.")
        if name.startswith("gsd-") and "repository" in entry:
            for path in target.rglob("*.md"):
                content = path.read_text(encoding="utf-8")
                content = content.replace("~/.claude/gsd-core", (root / "gsd-core").as_posix())
                content = content.replace("$HOME/.claude/gsd-core", (root / "gsd-core").as_posix())
                path.write_text(content, encoding="utf-8")
            adaptations.append("Resolved GSD workflow references to the pinned canonical source checkout; no hooks/config installed.")
        if name.startswith("psy-ana-"):
            skill.write_text(skill.read_text().replace("../SKILL.md", (root / "amazing-psycoder/SKILL.md").as_posix()), encoding="utf-8")
            adaptations.append("Resolved parent contract to pinned source checkout, retaining its shared validation scripts.")
        if name in ("grammar-of-graphics-and-declarative-visualization", "statistical-and-uncertainty-visualization"):
            shared = root / "plugins/build-web-data-visualization/references"
            import shutil
            shutil.copytree(shared, target / "references/shared")
            for path in target.rglob("*.md"):
                content = path.read_text(encoding="utf-8")
                # Source shared foundation links now have a self-contained owner.
                content = content.replace("../../references/foundations/", "./references/shared/foundations/") if path == skill else content
                path.write_text(content, encoding="utf-8")
            adaptations.append("Bundled shared visualization foundations.")
        for license_name in ("LICENSE", "LICENSE.md", "LICENSE.txt"):
            license_path = root / license_name
            if license_path.is_file() and source != root:
                import shutil
                shutil.copyfile(license_path, target / ("UPSTREAM-" + license_name))
                break
        if name.startswith(("gsd-", "superpowers-")):
            skill.write_text(skill.read_text() + "\n\n## Codex installation scope\n\nUse the active harness's tools, model allowlist, permissions and user authorization.\nToolkit tool names and delegation examples do not override them. These are skill\nassets; installing them does not enable hooks, change configuration or authorize\nexternal messages, autonomous delegation or package execution. GSD CLI build and\noptional integrations are separate runtime capabilities, not verified by this install.\n", encoding="utf-8")
        ok, reason = validator.validate_skill(target)
        if not ok:
            raise RuntimeError(name + ": " + reason)
        files = {p.relative_to(target).as_posix(): sha256(p.read_bytes()).hexdigest()
                 for p in target.rglob("*") if p.is_file()}
        receipt = {k: v for k, v in entry.items() if k in ("name", "repository", "commit", "subdirectory")}
        if "local_source" in entry:
            receipt["source"] = "Existing reviewed " + ("For-AI bundled companion" if name.startswith(("agents-inc-", "mobx-")) else "project fallback")
        receipt.update(adaptations=adaptations, files_sha256=files, validation="PASS")
        (target / "INSTALLATION.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        receipts.append(receipt)
        print("Installed and validated " + name, flush=True)
    record = dict(date="2026-10-23", scope="Missing Study5_Publication routed user-level skills",
                  assets_only=True, hooks_or_config_changed=False, installed=receipts,
                  unresolved={"consensus-mcp": "No exact upstream skill found; configured Consensus connector remains available. Do not substitute an unrelated consensus skill."},
                  gsd_runtime="Pinned workflow assets available; CLI compiled runtime not installed or executed.")
    output = project / "for-ai/orchestration/project_skills_installation.json"
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Installed {len(receipts)} skills; receipt: {output}")


if __name__ == "__main__":
    install()
