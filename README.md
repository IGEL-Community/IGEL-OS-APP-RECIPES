# IGEL-OS-APP-RECIPES

[Getting Started with the IGEL OS App Recipes](utils/Getting-Started-with-the-IGEL-OS-App-Recipes.pdf)

-----

-----

## Tutorial

[Video: Introduction](utils/videos/01-HOWTO-Introduction.mp4?raw=true)

[IGEL Community Docs: HOWTO GitHub with Microsoft Visual Studio Code](https://igel-community.github.io/IGEL-Docs-v02/Docs/HOWTO-GitHub-with-VS-Code/)


-----

-----

##  Set apptype to 2.3 in app.json file

**NOTE:** The community Apps that are based on a recipe and vendor binary need to have a special apptype, which is 2.3.

```bash linenums="1"
"apptype": 2.3,
  "architectures": [
    "x64"
  ],
```

Current valid App Types:

- Type 0 - IGEL Base OS
- Type 1 - IGEL Created apps - Chromiums, CWA, Teams PWA, Zoom Desktop
- Type 2.1 - IGEL Ready Certified Apps
- Type 2.2 - Customer private app
- Type 2.3 - IGEL Community Recipe apps - applications which are based on IGEL Community recipe and vendor binary
- Type 2.4 - IGEL Community apps

-----

-----

## Getting Started With the IGEL OS App Recipes

This document provides you with the basic knowledge that is required to create an IGEL OS App with igelpkg.

Basically, the procedure is as follows:

- Install the IGEL OS App SDK on a Linux system.
- Build and test your app.

-----

## Prerequisites

- Machine with Ubuntu Linux 18.04 or higher, or another Debian-based Linux distribution
- The IGEL OS APP SDK, version 0.9.8 or higher
- Device with IGEL OS 12.01.120. To test if the app can be installed and started, a virtual machine is sufficient. If 3D graphics are required, a hardware device might be a good choice. To test if an app can be installed and started, a virtual machine is sufficient.
- A local terminal is configured on the device

-----

## Installing igelpkg

- Copy the files igel-build-tools-static[version]_amd64.deb and igelpkg_[version]_amd64.deb to your development machine.
- Go to the directory that contains the files and enter the following command:

```bash linenums="1"
sudo apt install ./igel-build-tools-static[version]_amd64.deb igelpkg_[version]_amd64.deb
```

- To show the general help, enter

```bash linenums="1"
igelpkg --help
```

- To get help for a specific module, enter the module's name and then --help, for instance:

```bash linenums="1"
igelpkg build --help
```