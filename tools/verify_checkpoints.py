"""Integrity verifier for frozen checkpoints — automates the 'immutability is the witness' claim.

For every checkpoint it re-derives each artifact's sha256 and compares it to the value frozen
in MANIFEST.json, validates every .json artifact parses, and checks the manifest schema. Any
post-hoc edit of frozen evidence (the one thing the whole experiment relies on NOT happening)
fails the run. Pure stdlib; safe to wire into CI.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CKPT = ROOT / "checkpoints"
# Core keys present since the first checkpoint. `errors` was added later (PR #1) so it is not
# required here — old snapshots legitimately predate it; their artifact hashes still verify.
MANIFEST_KEYS = {"checkpoint", "created_utc", "git_head", "artifacts"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def verify_checkpoint(d: Path) -> list[str]:
    """Return a list of integrity problems for one checkpoint dir (empty == clean)."""
    problems: list[str] = []
    mf = d / "MANIFEST.json"
    if not mf.exists():
        return [f"{d.name}: MANIFEST.json missing"]
    try:
        m = json.loads(mf.read_text())
    except json.JSONDecodeError as e:
        return [f"{d.name}: MANIFEST.json invalid JSON ({e})"]

    missing_keys = MANIFEST_KEYS - m.keys()
    if missing_keys:
        problems.append(f"{d.name}: MANIFEST missing keys {sorted(missing_keys)}")

    for name, frozen_hash in (m.get("artifacts") or {}).items():
        f = d / name
        if not f.exists():
            problems.append(f"{d.name}/{name}: listed in MANIFEST but file missing")
            continue
        actual = sha256(f)
        if actual != frozen_hash:
            problems.append(f"{d.name}/{name}: TAMPERED — sha {actual} != frozen {frozen_hash}")

    for jf in d.glob("*.json"):
        try:
            json.loads(jf.read_text())
        except json.JSONDecodeError as e:
            problems.append(f"{d.name}/{jf.name}: invalid JSON ({e})")
    return problems


def main(ckpt: Path = CKPT) -> int:
    dirs = sorted(p for p in ckpt.iterdir() if p.is_dir())
    all_problems: list[str] = []
    for d in dirs:
        all_problems += verify_checkpoint(d)
    if all_problems:
        print(f"checkpoint integrity: {len(all_problems)} problem(s) across {len(dirs)} checkpoints:",
              file=sys.stderr)
        for p in all_problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"checkpoint integrity: {len(dirs)} checkpoints clean (hashes match MANIFEST)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
