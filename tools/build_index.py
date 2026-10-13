"""Rebuilds index.json - the list the app downloads - from the package files in packages/, and remembers who published
each id (owners.json). Run by .github/workflows/build-index.yml after every merge; nobody edits index.json by hand.

    python build_index.py [--submitter <GitHub login of whoever added the new packages>]

external.json (optional, same shape as index.json) lists packages hosted elsewhere; its entries are added as they are.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RAW_BASE = "https://raw.githubusercontent.com/%s/%s/" % (os.environ.get("GITHUB_REPOSITORY", "pieterjanpintens/descent-engine-community"),
                                                         os.environ.get("CATALOG_BRANCH", "main"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--submitter", default="")
    options = parser.parse_args()

    owners = catalog.load_json(os.path.join(ROOT, "owners.json"), {})
    entries = []
    skipped = 0
    packages_root = os.path.join(ROOT, catalog.PACKAGES_DIR)
    for folder in sorted(os.listdir(packages_root)) if os.path.isdir(packages_root) else []:
        if not os.path.isdir(os.path.join(packages_root, folder)):
            continue
        for file_name in sorted(os.listdir(os.path.join(packages_root, folder))):
            relative = "%s/%s/%s" % (catalog.PACKAGES_DIR, folder, file_name)
            match = catalog.PATH_PATTERN.match(relative)
            if not match:
                continue
            path = os.path.join(ROOT, relative)
            try:
                manifest = catalog.read_manifest(path)
            except ValueError as reason:
                print("skipped %s: %s" % (relative, reason))
                skipped += 1
                continue
            package_id, version = match.group(2), match.group(3)
            if str(manifest.get("id", "")) != package_id or str(manifest.get("version", "")) != version or manifest.get("type") not in ("mission", "campaign"):
                print("skipped %s: the manifest does not match the file name" % relative)
                skipped += 1
                continue
            if package_id not in owners and options.submitter:
                owners[package_id] = options.submitter
            entries.append({
                "id": package_id,
                "type": manifest["type"],
                "name": str(manifest.get("name", package_id))[:80],
                "author": str(manifest.get("author", ""))[:60] or owners.get(package_id, ""),
                "description": str(manifest.get("description", ""))[:600],
                "version": version,
                "url": RAW_BASE + relative,
                "sha256": catalog.sha256_of(path),
                "size_bytes": os.path.getsize(path),
            })
    external = catalog.load_json(os.path.join(ROOT, "external.json"), {"packages": []})
    entries.extend(entry for entry in external.get("packages", []) if isinstance(entry, dict))
    entries.sort(key=lambda entry: (str(entry.get("name", "")).lower(), str(entry.get("id", "")), catalog.version_key(str(entry.get("version", "0")))))

    with open(os.path.join(ROOT, "index.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump({"format": 1, "packages": entries}, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    with open(os.path.join(ROOT, "owners.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(sorted(owners.items())), handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print("index.json: %d package(s), %d skipped; owners.json: %d id(s)" % (len(entries), skipped, len(owners)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
