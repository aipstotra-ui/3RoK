"""Create and check data-release manifests (ADR 0005).

A manifest lists every asset in a GitHub data release with its size and sha256,
plus where the data came from, so anyone can prove a download is unaltered.

Usage:
    python -m orbitlife_build.manifest create --release data-v0 --generator ... \
        --source ... --license ... --out manifest.json FILE [FILE ...]
    python -m orbitlife_build.manifest verify manifest.json DIR
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tarfile
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
_CHUNK_BYTES = 1 << 20


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(_CHUNK_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def _tar_members(path: Path) -> list[dict[str, Any]]:
    """Per-file sha256 for every regular file inside a tar archive."""
    members: list[dict[str, Any]] = []
    with tarfile.open(path) as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            extracted = archive.extractfile(member)
            if extracted is None:
                continue
            digest = hashlib.sha256()
            while chunk := extracted.read(_CHUNK_BYTES):
                digest.update(chunk)
            members.append(
                {"path": member.name, "size_bytes": member.size, "sha256": digest.hexdigest()}
            )
    return sorted(members, key=lambda m: str(m["path"]))


def build_manifest(
    files: Iterable[Path],
    *,
    release: str,
    generator: str,
    source: str,
    license_note: str,
) -> dict[str, Any]:
    assets = []
    for path in sorted(files, key=lambda p: p.name):
        entry: dict[str, Any] = {
            "name": path.name,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        if tarfile.is_tarfile(path):
            entry["contents"] = _tar_members(path)
        assets.append(entry)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "release": release,
        "created_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": generator,
        "source": source,
        "license": license_note,
        "assets": assets,
    }


def verify_manifest(manifest: dict[str, Any], directory: Path) -> list[str]:
    """Return a list of problems; an empty list means every asset matches."""
    problems: list[str] = []
    for asset in manifest["assets"]:
        path = directory / asset["name"]
        if not path.is_file():
            problems.append(f"{asset['name']}: missing")
            continue
        if path.stat().st_size != asset["size_bytes"]:
            problems.append(f"{asset['name']}: size mismatch")
        if sha256_file(path) != asset["sha256"]:
            problems.append(f"{asset['name']}: sha256 mismatch")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m orbitlife_build.manifest")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="write a manifest for release assets")
    create.add_argument("files", nargs="+", type=Path)
    create.add_argument("--release", required=True)
    create.add_argument("--generator", required=True)
    create.add_argument("--source", required=True)
    create.add_argument("--license", dest="license_note", required=True)
    create.add_argument("--out", type=Path, required=True)

    verify = sub.add_parser("verify", help="check downloaded assets against a manifest")
    verify.add_argument("manifest", type=Path)
    verify.add_argument("directory", type=Path)

    args = parser.parse_args(argv)
    if args.command == "create":
        manifest = build_manifest(
            args.files,
            release=args.release,
            generator=args.generator,
            source=args.source,
            license_note=args.license_note,
        )
        args.out.write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"wrote {args.out} ({len(manifest['assets'])} assets)")
        return 0

    manifest = json.loads(args.manifest.read_text())
    problems = verify_manifest(manifest, args.directory)
    for problem in problems:
        print(f"FAIL {problem}")
    if problems:
        return 1
    print(f"OK: all {len(manifest['assets'])} assets match {manifest['release']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
