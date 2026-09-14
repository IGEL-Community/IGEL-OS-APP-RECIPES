# ONLYOFFICE Desktop Editors

Community recipe for ONLYOFFICE Desktop Editors on IGEL OS 12, based on the LibreOffice session configuration in this repository.

## Build with App Creator Portal

1. Download `APP_Packages/Office/onlyoffice_community.zip` from this repository.
2. Download the pinned [ONLYOFFICE 9.4.0 Linux amd64 Debian package](https://github.com/ONLYOFFICE/DesktopEditors/releases/download/v9.4.0/onlyoffice-desktopeditors_amd64.deb).
3. Upload the recipe ZIP in Step 1 of [IGEL App Creator Portal](https://appcreator.igel.com).
4. Upload `onlyoffice-desktopeditors_amd64.deb` in Step 2, keeping that filename.
5. Build for x64 using Debian Bookworm. Download the resulting signed app and certificate, then deploy through UMS according to the [IGEL instructions](https://kb.igel.com/igel-app-creator/current/igel-app-creator-portal).

Vendor version: **9.4.0-129**. Recipe version: **9.4.0+129.2**.

SHA-256 of the vendor Debian package:

```
4271434e81be42b1559fd989d24bf6d413482f278dc6a5e328202a4fc1a18649
```

The `/releases/latest/download/` URL may change. Use the pinned release above with this recipe. The vendor binary is not included in this repository.

## Integration

- IGEL session configuration uses the standard session page and shortcut settings.
- The launcher runs the application from `/services/onlyoffice/opt/onlyoffice/desktopeditors`, forwards file arguments and selects the vendor's bundled Qt libraries/plugins.
- Desktop file associations and new-document actions are retained. Default associations are not forcibly changed.
- The shipped Qt build uses X11; a Wayland session requires Xwayland.
- Original binary permissions are retained and stripping is disabled. No `--no-sandbox` option is added.
- The optional Qt virtual-keyboard plugin is excluded because its Qt Quick/QML dependencies are not bundled. Physical keyboard, compose and IBus support remain.

## Persistent data

The writable partition uses `large`, `compressed` and `prefer_btrfs`. These directories are persistent, with the IGEL community recipe's user ownership `777:100`:

- `/userhome/.config/onlyoffice`: preferences.
- `/userhome/.local/share/onlyoffice`: application data and recovery files.
- `/userhome/OnlyOfficeDocuments`: local documents.

Save local documents explicitly into `/userhome/OnlyOfficeDocuments` or another managed persistent location. The recipe does not change the default save location or take ownership of the shared `/userhome/Documents` directory. Persistent storage is not a backup.

## Dependencies and license metadata

`igel/debian.json` provides Bookworm supplemental libraries, fonts and GStreamer codecs. `DEPENDENCIES.json` records the dependency selection and libraries expected from the Base System. Validate those assumptions against your target Base System before deployment. The vendor payload expands to approximately 1.23 GiB, plus approximately 233 MiB of supplemental packages before IGEL compression and writable storage.

Explicit copyright metadata is provided for the 23 Debian packages whose licenses were not detected automatically by App Creator. Most entries reference their extracted Debian copyright files. The libgfortran5, libgomp1 and libquadmath0 documentation directories point to gcc-12-base; their entries embed the complete gcc-12-base copyright notice from version 12.2.0-14+deb12u1 so they do not depend on a missing documentation symlink target. Refresh these notices when updating those packages. Custom `Debian-copyright-*` names identify the supplied notices, not alternative licenses.

## Validation

The contributor reports that App Creator built revision 2 successfully after the license metadata correction. Local checks covered the published vendor SHA-256, all 4,664 vendor file checksums, launcher argument forwarding, JSON/session references and standard ZIP format. Endpoint GUI, persistence, printing and media functionality still require validation on the deployed IGEL OS version. This is a community recipe, not an IGEL Ready certification.

## Licenses

ONLYOFFICE's Debian package declares AGPL-3.0-only. Vendor license and copyright notices are retained. `LICENSE.recipe` preserves the MIT notice for recipe material derived from the community LibreOffice example. The generic recipe icons do not replace the application's own branding.
