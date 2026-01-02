# IGEL-OS-APP-RECIPES

-----

-----

**Please Note:** 

- The IGEL App Creator portal runs the IGEL SDK to create and sign your application for OS12
- For security requirements, the IGEL App Creator Portal only allows for debian and ubuntu official repository URLs. Use the file upload feature to add file.
- For OS 12.5.0+ you may need to have the app `Compatibility layer for 12.0.x apps` installed
- UMS Web App - Apps Settings: `Download from UMS` and do not set `Block devices from downloading apps from the public App Portal as a fallback option` unless there is no internet access from OS 12 devices
- Using the UMS update proxy and distributing OS 12 apps through `ICG is not supported`. As an alternative, you can use a `reverse proxy` between IGEL OS devices and UMS. 

-----

-----

- [IGEL SDK Reference Manual](utils/IGEL-SDK-Reference-Manual.pdf)

**NOTE:**  The IGEL SDK is not needed for creating recipes. The IGEL SDK Reference Manual provides details on files and format of files used in recipes.

- <a href="utils/igelpkg-new-template-1.0.0.zip" download> IGEL SDK: Initial Data Structure Template</a>

- With SDK ≥1.0.0 and IGEL OS ≥ 12.5.0 it is no longer necessary to use a special Developer Edition of IGEL OS.

- To develop and evaluate apps, it is now sufficient to copy the two public SDK app signing keys to the IGEL OS:

    - copy `/usr/share/igelpkg/certs/IGEL_OS_12_SDK-intermediate.crt` from development machine to `/wfs/cmty/im-certs/` on IGEL OS
    - deploy `/usr/share/igelpkg/certs/IGEL_OS_12_SDK-leaf.crt` as app signing certificate by UMS
    - reboot

- SDK command to build and sign app:

```bash linenums="1"
igelpkg build -r bookworm -a x64 -sp -sa
```

-----

-----

## Tutorial

- [Video: Introduction](utils/videos/01-HOWTO-Introduction.mp4?raw=true)

- [Video: IGEL App Creator Portal - Steps to build SpeedCrunch](https://igel-community.github.io/IGEL-Docs-v02/Docs/HOWTO-Channel-Demos/#igel-app-creator-portal-steps-to-build-speedcrunch)

- [IGEL Community Docs: HOWTO GitHub with Microsoft Visual Studio Code](https://igel-community.github.io/IGEL-Docs-v02/Docs/HOWTO-GitHub-with-VS-Code/)

-----

-----

## Changing version in APP.JSON

- The technical version of the app is defined in the field `version`.

- The version numbers must comply with the [Semantic Versioning (SemVer) specifications](https://semver.org/)

- Version example used for IGEL OS Base OS:

```bash linenums="1"
      base_system-12.6.0
      base_system-12.6.0+1
      base_system-12.6.0+2
      base_system-12.6.1-0.tp.3
      base_system-12.6.1-0.tp.4
      base_system-12.6.1-1.rc.2
      base_system-12.6.1-1.rc.3
      base_system-12.7.0-0.tp.2
      base_system-12.7.0-0.tp.3
```

-----

-----

## Build your own IGEL OS App 

- [IGEL App Creator Portal – the straightforward way to secure and deploy your third-party apps to IGEL OS12](https://www.igel.com/blog/igel-app-creator-portal-the-straightforward-way-to-secure-and-deploy-your-third-party-apps-to-igel-os12/)
- [IGEL KB: IGEL App Creator Portal](https://kb.igel.com/igel-app-creator/current/igel-app-creator-portal)
- [IGEL KB: Upload and Assign Files in the IGEL UMS Web App - Classification - App signing certificate](https://kb.igel.com/en/universal-management-suite/current/upload-and-assign-files-in-the-igel-ums-web-app)
- [IGEL Community - IGEL App Creator Portal](https://igel-community.github.io/IGEL-Docs-v02/Docs/HOWTO-Add-Applications/#igel-app-creator-portal)
- [SPDX License List](https://spdx.org/licenses/) enables the efficient and reliable identification of license type
- [How to use IGEL App Creator SDK Docker Container](https://igel-community.github.io/IGEL-Docs-v02/Docs/HOWTO-Docker/)

-----

## How to add links to /services/application_name

The App Creator Portal has automatic linking function that recognizes well-known folders that follow a common standard. Mostly libraries, desktop files, udev rules.

For special links, they are created via a system service file. The path to place the file is:

```bash linenums="1"
input/all/etc/systemd/system/appname.service
```

If your recipe already has a .service file in our app just add a line:

```bash linenums="1"
ExecStartPre=/bin/ln -sf /services/citrix_nsgclient/opt/Citrix/NSGClient /opt/Citrix/NSGClient
```

Otherwise create a .service file with:

```bash linenums="1"
[Unit]
Description=My app Service

[Service]
ExecStart=/bin/ln -sf /services/citrix_nsgclient/opt/Citrix/NSGClient /opt/Citrix/NSGClient
```

To enable the service create the file `igel/install.sh` and add:

```bash linenums="1"
#!/bin/bash
enable_system_service appname.service
```

-----

## Using Pre Package Commands

Pre packages commands can be placed into file `igel/pre_package_commands.sh`. This can be used to create files / folders as part of the recipe.

Example, used in recipe for `Topaz Systems SigPlus Pro C++ Object Library`, of using `igel/pre_package_commands.sh` to make a directory and create a file.

```bash linenums="1"
#!/bin/bash

mkdir -p "%root%/etc/topaz"
cat <<"EOF" > "%root%/etc/topaz/topaz-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="app-topaz${1}"

# app path
APP_PATH="/services/topaz_sigplus_pro_c_object_library"

# output to systemlog with ID amd tag
LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

# Linking files and folders on proper path
find ${APP_PATH} -printf "/%P\n" | while read DEST
do
  if [ ! -z "${DEST}" -a ! -e "${DEST}" ]; then
    # Remove the last slash, if it is a dir
    [ -d $DEST ] && DEST=${DEST%/} | $LOGGER
    if [ ! -z "${DEST}" ]; then
      ln -sv "${APP_PATH}/${DEST}" "${DEST}" | $LOGGER
    fi
  fi
done

echo "Finished" | $LOGGER

EOF
```

-----

-----

## Use prefer_btrfs file system for read / write partition

**Note:** Some apps may not work with non-btrfs file system for read / write partition. Applications, like 1Password and OneDrive, use SQLite, an Open-Source database program that uses a sub-set of the SQL database descriptor language, in their application and does not work with NTFS file system.

***Update:** 2 June 2025, the issue with SQLite on NTFS was with compression enabled.

- In the `app.json` file set `prefer_btrfs` as the file system

```json
"rw_partition": {
  "size": "small",
  "flags": [
    "compressed",
    "prefer_btrfs"
  ]
}
```

- Check file system used for `/services_rw/*`

```bash linenums="1"
df -Th | grep services_rw
```

-----

-----

## Partition Size

The partition size can be defined with the key size. The following values are possible:

- small
- medium
- large
- Exact size in KiB without quotes.

When small, medium, or large are defined, the size is calculated depending on the device's storage size.

To create a 2GB partition:

```json linenums="1"
"rw_partition": {
  "size": 2000000
},
```

-----

-----

## Allow Execute Permission from read / write Partition

The small partition will allow for execution of programs

```json
"rw_partition": {
  "size": "small",
  "flags": [
    "allow_execute"
  ]
}
```

-----

-----

## Listing Systemd Targets

- List all the systemd targets on system:

```bash linenums="1"
systemctl list-units --type target
```

-----

-----
