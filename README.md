# Descent Engine - community catalog

The list of missions and campaigns shared by players of [Descent Engine](https://github.com/pieterjanpintens/descent-engine).
This repository holds the list and the shared packages; the app is in the game repository.

`index.json` is the list of missions and campaigns that players shared. The game downloads it from this repository
(main menu > Community > Browse online) and shows what is in it. Players need no account. Additions go through a pull request, so
somebody looks at every one of them.

## Share something

**From the app (the easy way)**

1. In the mission editor or campaign editor choose **File > Export package…**, fill in the details and save the `.descentpkg` file.
2. Press **Publish to the community…** in the dialog that follows (or later: main menu > Community > *Publish a package file…*).
3. The first time, sign in with GitHub: the app shows a short code, you type it on github.com. No password goes through the app.
   GitHub asks for permission to write to your public repositories - the app only uses it for your copy (fork) of this repository.
4. The app sends your package here as a pull request. It is checked automatically, and once it is approved it appears in everyone's
   Community page. You don't have to edit anything by hand.

Sharing an update: raise the **version** in the export dialog and publish again. Every version is installed **next to** the others on
a player's computer - nothing is ever updated in place, so saved games and edits are never touched. A published version is never
changed or removed.

A package name belongs to the GitHub account that first published it: nobody else can publish a new version under the same id.

Packages with pictures: only share pictures you made or may share. The export dialog asks you to confirm this.

**By hand**

Open a pull request that adds your file as `packages/<id>/<id>-<version>.descentpkg` (the id and version are in the file name the
export dialog proposes). Nothing else needs changing. A package hosted somewhere else can be listed in `external.json`
(same shape as `index.json`).

## How this repository works

- `packages/` - the shared packages, one folder per id.
- `index.json` - the list the app downloads. It is **rebuilt automatically** after every merge (`tools/build_index.py`); don't edit it.
- `owners.json` - which GitHub account published each id (also kept automatically).
- Every pull request is checked twice: it may only *add* package files, by their owner (`tools/check_submission.py`), and every package
  must pass the app's own package check - the same one that runs before a player installs anything.

## What a package may contain

A package is only **data**: one mission file, or a campaign (its mission files and pictures). Before anything is installed the app reads every
file as plain text and refuses anything that could load code or other files (other scripts, scenes, embedded scripts, objects), and checks the
zip itself (sizes, names, file types). If you build a package by hand and it is refused, the message says why.
