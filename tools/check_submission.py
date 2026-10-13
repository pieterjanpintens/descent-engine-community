"""Checks a pull request before anyone looks at it (run by .github/workflows/check-submission.yml from the TRUSTED copy of
this repository, against the submitted copy).

A submission may only ADD package files, each as packages/<id>/<id>-<version>.descentpkg, whose manifest says the same id
and version. An id belongs to the GitHub account that first published it (owners.json): somebody else cannot publish a
new version of it. The package's CONTENT is checked separately by the app's own validator (the "validate" job).

    python check_submission.py --repo <submitted checkout> --base <base commit> --author <GitHub login>
"""

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--author", required=True)
    parser.add_argument("--owners", help="owners.json of the trusted copy (default: next to this script's repository)")
    options = parser.parse_args()
    owners_path = options.owners or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "owners.json")
    owners = catalog.load_json(owners_path, {})

    changed = subprocess.run(["git", "-C", options.repo, "diff", "--name-status", "--no-renames", "%s...HEAD" % options.base],
                             capture_output=True, text=True, check=True).stdout.splitlines()
    problems = []
    packages = 0
    for line in changed:
        status, _tab, path = line.partition("\t")
        match = catalog.PATH_PATTERN.match(path)
        if not match:
            problems.append("%s: a submission may only add package files (packages/<id>/<id>-<version>.descentpkg)" % path)
            continue
        if status != "A":
            problems.append("%s: published packages are never changed or removed - publish a new version instead" % path)
            continue
        folder_id, file_id, version = match.groups()
        if folder_id != file_id:
            problems.append("%s: the folder and the file name must carry the same id" % path)
            continue
        owner = owners.get(file_id)
        if owner and owner.lower() != options.author.lower():
            problems.append("%s: \"%s\" was published by %s - only they can publish new versions of it (choose another name or author)" % (path, file_id, owner))
            continue
        try:
            manifest = catalog.read_manifest(os.path.join(options.repo, path))
        except ValueError as reason:
            problems.append("%s: %s" % (path, reason))
            continue
        if str(manifest.get("id", "")) != file_id or str(manifest.get("version", "")) != version:
            problems.append("%s: the package says it is %s %s - the file name must match" % (path, manifest.get("id"), manifest.get("version")))
            continue
        packages += 1
        print("ok  %s  (%s %s, a %s by %s)" % (path, manifest.get("name"), version, manifest.get("type"), manifest.get("author") or options.author))

    if not changed:
        problems.append("the pull request changes nothing")
    for problem in problems:
        print("PROBLEM  " + problem)
    print("%d package(s) added, %d problem(s)" % (packages, len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
