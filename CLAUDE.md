# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Community-maintained recipes for building IGEL OS 12 custom apps. Recipes are structured directory trees that define everything needed to convert Debian packages into IGEL packages (`.ipkg`) via the IGEL App Creator Portal or the IGEL SDK (`igelpkg` CLI). The IGEL SDK is not required for creating recipes — the App Creator Portal handles building and signing.

## Workflow & Git Conventions

- **All changes via PR** to `main` — delete the PR branch after merge
- **CI auto-builds zips** on push to `main` (`.github/workflows/master.yml` runs `utils/make-app-packages.sh`) — only changed apps get re-zipped
- **Never manually edit** anything in `APP_Packages/` — those zips are CI-generated
- Output naming: `APP_Packages/{Category}/{appname}_community.zip`

## Repository Structure

- `APP_Source/{Category}/{appname}/` — recipe source (the only directory humans edit)
- `APP_Packages/{Category}/` — CI-generated zip packages (do not modify)
- `utils/` — build script, new-recipe template, SDK reference manual, helper scripts
- **Categories:** Apps, Browsers, Multimedia, Network, Office, Scripts, Server, Tools_Drivers, Unified_Communications

## Recipe Anatomy

Every recipe lives in `APP_Source/{Category}/{appname}/` with this structure:

### Required Files

| File | Purpose |
|---|---|
| `app.json` | App manifest: name, version (SemVer), author, vendor, categories, icons, summary, `rw_partition` settings |
| `igel/install.json` | File extraction rules — regex source matching, owner (`uid:gid`), permissions (octal), strip option. Commonly excludes `usr/share/doc`, `usr/share/man`, `usr/share/metainfo` |
| `data/app.png` (or `.svg`) | Color application icon |
| `data/monochrome.png` (or `.svg`) | Monochrome icon variant |
| `data/descriptions/en` | English app description |
| `data/changelogs/en` | Debian-format changelog |

### Optional Files

| File | Purpose |
|---|---|
| `igel/thirdparty.json` | Third-party binary declarations with URLs and licenses. Uses `file:///tmp/` for uploaded binaries |
| `igel/debian.json` | Debian/Ubuntu repo package dependencies (array of `{"package": "name"}`) |
| `igel/dirs.json` | Persistent directories that survive reboots (e.g., `{"path": "/userhome/.config/app", "persistent": true, "owner": "777:100"}`) |
| `igel/install.sh` | Post-install script — typically calls `enable_system_service appname.service` |
| `igel/pre_package_commands.sh` | Build-time script to create files/dirs. Uses `%root%` placeholder for package root |
| `igel/ignore.json` | Files to exclude from packaging |
| `igel/input.json` | Input configuration |
| `data/config/config.param` | IGEL session configuration (XML-like format with `<appname%>` base / `<appname0>` instances) |
| `data/config/ui.json` | UMS UI tree structure for app configuration |
| `data/config/translation.json` | Localization strings (English required, German common) |
| `input/all/` | Filesystem overlay — files here map to their target paths on the device |
| `input/all/config/sessions/{appname0}` | Bash launch script for app sessions |
| `input/all/etc/systemd/system/{appname}.service` | Systemd service unit file |

## Key Conventions

- **Naming:** lowercase with underscores for app directory names and `name` field in `app.json`
- **Versioning:** SemVer format `{app_version}+{igel_build_number}` (e.g., `8.12.6+1.0`)
- **Mount paths:** apps at `/services/{appname}` (read-only), `/services_rw/{appname}` (read-write)
- **User data:** persistent dirs typically at `/userhome/.config/{appname}`
- **rw_partition sizes:** `small`, `medium`, `large`, or exact KiB integer (e.g., `2000000` for ~2GB)
- **rw_partition flags:** `compressed`, `prefer_btrfs`, `allow_execute`
- **SQLite apps** need `prefer_btrfs` — SQLite does not work with NTFS compression
- **Symlinks** to `/services/{appname}/...` created via `ExecStartPre` in systemd service files or via the App Creator Portal's automatic linking for well-known folders
- **Logging:** use `logger -it ${ACTION}` for systemlog output in init scripts

## Creating a New Recipe

1. Start from template: `utils/igelpkg-new-template-1.0.0.zip`
2. Place in `APP_Source/{Category}/{appname}/`
3. Build with SDK: `igelpkg build -r bookworm -a x64 -sp -sa`

For SDK development (OS >= 12.5.0): copy SDK signing keys to device — no Developer Edition needed.

## Key References

- [IGEL SDK Reference Manual](utils/IGEL-SDK-Reference-Manual.pdf) — detailed file format documentation
- [IGEL App Creator Portal](https://kb.igel.com/igel-app-creator/current/igel-app-creator-portal)
- [IGEL Community Docs](https://igel-community.github.io/IGEL-Docs-v02/)
- [SPDX License List](https://spdx.org/licenses/) — for license identifiers in thirdparty.json
