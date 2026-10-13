"""Shared by check_submission.py and build_index.py: where packages live and how their manifest is read."""

import hashlib
import json
import os
import re
import zipfile

EXTENSION = "descentpkg"
PACKAGES_DIR = "packages"
MAX_PACKAGE_BYTES = 64 * 1048576
MAX_MANIFEST_BYTES = 64 * 1024
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,79}$")
VERSION_PATTERN = re.compile(r"^[0-9]+(\.[0-9]+){0,3}$")
PATH_PATTERN = re.compile(r"^packages/([a-z0-9][a-z0-9._-]{0,79})/([a-z0-9][a-z0-9._-]{0,79})-([0-9]+(?:\.[0-9]+){0,3})\.descentpkg$")


def read_manifest(path: str) -> dict:
    """The manifest.json of a package file. Raises ValueError with a readable reason."""
    if os.path.getsize(path) > MAX_PACKAGE_BYTES:
        raise ValueError("the package is larger than %d MB" % (MAX_PACKAGE_BYTES // 1048576))
    try:
        with zipfile.ZipFile(path) as archive:
            info = archive.getinfo("manifest.json")
            if info.file_size > MAX_MANIFEST_BYTES:
                raise ValueError("manifest.json is too large")
            manifest = json.loads(archive.read(info).decode("utf-8"))
    except (zipfile.BadZipFile, KeyError, UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("it is not a package (no readable manifest.json)")
    if not isinstance(manifest, dict):
        raise ValueError("manifest.json is not an object")
    return manifest


def sha256_of(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def version_key(version: str):
    return [int(part) for part in version.split(".")]


def load_json(path: str, fallback):
    if not os.path.exists(path):
        return fallback
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)
