# Building the app SuperTuxKart

![SuperTuxKart](data/app.png)

This document describes how to build an app from the sources. If you want to build an app yourself from scratch follow the example in [Creating](Creating.md)

## Table of Contents
1. [Installing prerequisites](#prerequisites)
2. [Building](#building)
3. [Configuring signing](#configuring-signing)
4. [Signing](#signing)
5. [Installing](#installing)


## License

This project is licensed under the terms of Apache License 2.0, see [LICENSE](LICENSE)

## Prerequisites

We currently support Ubuntu 18.04 and newer. Install igelpkg as described in the document "Getting Started With the IGEL OS App SDK-v7.pdf" of the SDK.

## Building

Clone and build the app.
```bash
git clone https://github.com/IGELTechnologyGmbH/SuperTuxKart.git
cd SuperTuxKart
igelpkg build -r focal
```


## Configuring signing

To install the APP, it must have a valid signature.

```bash
unzip osc_sdk_12.00.900.1.zip
sudo cp sign.json /usr/share/igelpkg/config.d/
sudo mkdir /usr/share/igelpkg/keys/
sudo cp IGEL_OS_12_SDK /usr/share/igelpkg/keys/
sudo cp IGEL_OS_12_SDK.pub /usr/share/igelpkg/certs/
```

Edit /usr/share/igelpkg/config.d/sign.json as root.

```json
{
  "verify": [
    "/usr/share/igelpkg/certs/IGEL_OS_12_SDK.pub"
  ],
  "sign": {
    "dev": {
      "key": "/usr/share/igelpkg/keys/IGEL_OS_12_SDK"
    }
  }
}
```

## Signing

```bash
igelpkg sign -a -p igelpkg.output/supertuxkart-1.1.0.ipkg
```
The app is now signed and ready to install

## Installing

Copy the file igelpkg.output/supertuxkart-1.1.0.ipkg to an usb drive and install it.
```bash
igelpkgctl install -f /media/supertuxkart-1.1.0.ipkg
```
