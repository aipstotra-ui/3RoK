import hashlib
from pathlib import Path

from orbitlife_build.manifest import build_manifest, verify_manifest


def _write(path: Path, data: bytes) -> Path:
    path.write_bytes(data)
    return path


def test_manifest_records_size_and_sha256(tmp_path: Path) -> None:
    f = _write(tmp_path / "a.bin", b"hello")
    m = build_manifest(
        [f], release="data-v0", generator="test", source="unit test", license_note="none"
    )
    entry = m["assets"][0]
    assert m["release"] == "data-v0"
    assert entry["name"] == "a.bin"
    assert entry["size_bytes"] == 5
    assert entry["sha256"] == hashlib.sha256(b"hello").hexdigest()


def test_verify_passes_for_unchanged_files(tmp_path: Path) -> None:
    f = _write(tmp_path / "a.bin", b"hello")
    m = build_manifest([f], release="r", generator="g", source="s", license_note="l")
    assert verify_manifest(m, tmp_path) == []


def test_verify_detects_a_changed_file(tmp_path: Path) -> None:
    f = _write(tmp_path / "a.bin", b"hello")
    m = build_manifest([f], release="r", generator="g", source="s", license_note="l")
    f.write_bytes(b"hellO")
    problems = verify_manifest(m, tmp_path)
    assert len(problems) == 1
    assert "sha256 mismatch" in problems[0]


def test_verify_detects_a_missing_file(tmp_path: Path) -> None:
    f = _write(tmp_path / "a.bin", b"hello")
    m = build_manifest([f], release="r", generator="g", source="s", license_note="l")
    f.unlink()
    problems = verify_manifest(m, tmp_path)
    assert problems == ["a.bin: missing"]
