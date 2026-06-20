"""Checkpoint integrity verifier: clean snapshot passes; any tamper/missing/bad-JSON fails."""
import json

import verify_checkpoints as vc


def _mk(d, payload="hello"):
    d.mkdir()
    art = d / "data.json"
    art.write_text(json.dumps({"v": payload}))
    h = vc.sha256(art)
    (d / "MANIFEST.json").write_text(json.dumps({
        "checkpoint": d.name, "created_utc": "2026-06-18T00:00:00+00:00",
        "git_head": "deadbeef", "artifacts": {"data.json": h}, "errors": {}}))
    return d


def test_clean_checkpoint_passes(tmp_path):
    _mk(tmp_path / "2026-06-18-auto")
    assert vc.main(tmp_path) == 0


def test_tampered_artifact_detected(tmp_path):
    d = _mk(tmp_path / "2026-06-18-auto")
    (d / "data.json").write_text(json.dumps({"v": "edited after freeze"}))  # mutate post-freeze
    problems = vc.verify_checkpoint(d)
    assert any("TAMPERED" in p for p in problems)
    assert vc.main(tmp_path) == 1


def test_missing_artifact_detected(tmp_path):
    d = _mk(tmp_path / "2026-06-18-auto")
    (d / "data.json").unlink()
    assert any("file missing" in p for p in vc.verify_checkpoint(d))


def test_invalid_manifest_keys_detected(tmp_path):
    d = tmp_path / "2026-06-18-auto"
    d.mkdir()
    (d / "MANIFEST.json").write_text(json.dumps({"checkpoint": "x"}))
    assert any("missing keys" in p for p in vc.verify_checkpoint(d))


def test_bad_json_artifact_detected(tmp_path):
    d = _mk(tmp_path / "2026-06-18-auto")
    (d / "broken.json").write_text("{not valid json")
    assert any("invalid JSON" in p for p in vc.verify_checkpoint(d))
