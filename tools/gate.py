"""Run gate: exit non-zero if the latest checkpoint recorded any collection errors.

The checkpoint script never aborts on a single source failing (by design — it freezes
everything that did succeed). That keeps green runs green even when sources fail or return
empty. This gate runs AFTER the snapshot is committed, so the evidence is preserved, then
fails the job so GitHub surfaces a red run / notification instead of silent degradation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CKPT = Path(__file__).resolve().parents[1] / "checkpoints"


def latest_manifest() -> tuple[str, dict] | tuple[None, None]:
    best, best_ts, best_name = None, "", None
    for d in CKPT.iterdir():
        mf = d / "MANIFEST.json" if d.is_dir() else None
        if not mf or not mf.exists():
            continue
        m = json.loads(mf.read_text())
        ts = m.get("created_utc", "")
        if ts >= best_ts:
            best, best_ts, best_name = m, ts, d.name
    return (best_name, best) if best is not None else (None, None)


def main() -> int:
    name, m = latest_manifest()
    if m is None:
        print("gate: no checkpoint manifest found", file=sys.stderr)
        return 1
    errors = m.get("errors", {})
    if not errors:
        print(f"gate: {name} clean — no collection errors")
        return 0
    print(f"gate: {name} has {len(errors)} collection error(s):", file=sys.stderr)
    for src, msg in errors.items():
        print(f"  - {src}: {msg}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
