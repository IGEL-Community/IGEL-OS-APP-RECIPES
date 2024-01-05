# Creating the app SuperTuxKart from scratch

![SuperTuxKart](data/app.png)

## Prerequisites

We currently support Ubuntu 18.04 and newer. Install igelpkg as described in the document "Getting Started With the IGEL OS App SDK-v7.pdf" of the SDK. For the check for missing dependencies you will also need access to the app portal to download the base_system app.


## Creating the package structure

Create the package tree from template with version 1.1.0

```bash
igelpkg new -n supertuxkart -V 1.1.0
```

## Adding debian packages

Looking at https://packages.ubuntu.com/focal/supertuxkart we see that the names of the packages are supertuxkart and supertuxkart-data.

We need to add them to igel/debian.json

```json
[
  {
    "package": "supertuxkart"
  },
  {
    "package": "supertuxkart-data"
  },
]
```

## Building the app

We are ready to run the first build.

```bash
igelpkg build -r focal
```

## Checking for missing dependencies

Do a dependency check in order to find missing libraries. The base_system app is needed for the check, download the latest base_system app from the app portal.

```bash
igelpkg check igelpkg.output/supertuxkart-1.1.0.ipkg base_system-12.1.100+1.ipkg
```

Some libraries are missing:

```bash
Error [Checker]: supertuxkart-1.1.0_x64: usr/games/supertuxkart missing libmcpp.so.0
Error [Checker]: supertuxkart-1.1.0_x64: usr/games/supertuxkart missing libGLEW.so.2.1
Error [Checker]: supertuxkart-1.1.0_x64: usr/games/supertuxkart missing libsquish.so.0
Error [Checker]: supertuxkart-1.1.0_x64: usr/games/supertuxkart missing libopenal.so.1
Error [Checker]: supertuxkart-1.1.0_x64: usr/games/supertuxkart missing libraqm.so.0
```

## Adding missing dependencies

Now we search for the package names of the missing libraries. We need to do this for every missing library. Use https://packages.ubuntu.com to search for the package names.

E.g. for libmcpp.so.0:

https://packages.ubuntu.com/search?searchon=contents&keywords=libmcpp.so.0&mode=exactfilename&suite=focal&arch=any

shows libmcpp0, so we add that to igel/debian.json


```json
[
  {
    "package": "supertuxkart"
  },
  {
    "package": "supertuxkart-data"
  },
  {
    "package": "libmcpp0"
  },
  {
    "package": "libglew2.1"
  },
  {
    "package": "libsquish0"
  },
  {
    "package": "libopenal1"
  },
  {
    "package": "libraqm0"
  }
]
```

## Building the app again

We build the app again to find missing dependencies of the dependencies.
```bash
igelpkg build -r focal
```

## Fixing non-standard license for libmcpp0

Now igelpkg complains about a non-standard license of libmcpp0. For the other packages the license has been retrieved automatically.

We reference a copyright file from the libmcpp0 package in igel/debian.json.

```json
  {
    "package": "libmcpp0",
    "licenses": [
      {
          "name": "mcpp-2.7",
          "file": "%tmp%/usr/share/doc/libmcpp0/copyright"
      }
    ]
  },
```

## Building the app again
We build the app again to find missing dependencies of the dependencies.

```bash
igelpkg build -r focal
```

## Check missing dependencies

libsndio7.0 is missing which is a dependency of libopenal1.

```bash
igelpkg check igelpkg.output/supertuxkart-1.1.0.ipkg base_system-12.1.100+1.ipkg
```

```bash
Error [Checker]: supertuxkart-1.1.0_x64: usr/lib/x86_64-linux-gnu/libopenal.so.1.19.1 missing libsndio.so.7.0
```
We add that to igel/debian.json
```json
  {
    "package": "libsndio7.0"
  }
```


## Building the app again
Now we can build again. Additionally we use -sp to sign the package. When all missing dependencies are referenced, then the app can be signed.
```bash
igelpkg build -r focal -sp
```

## Installing
Install the app locally using igelpkgctl on the IGEL OS device. Best practice is to use a nfsmount or usb drive since this app is big and space on the device is limited.
```bash
igelpkgctl install -f supertuxkart-1.1.0.ipkg
```

## First start of the app
Now open a terminal as user and run the original binary.
```bash
/services/supertuxkart/usr/games/supertuxkart
```
We will notice that supertuxkart is complaining about missing fonts.

## Add missing fonts

Again we use https://packages.ubuntu.com to search for the package names.
We will need a few cycles of add fonts to debian.json, build, install and run to find all missing font packages.

igel/debian.json
```json
  {
    "package": "fonts-cantarell"
  },
  {
    "package": "fonts-noto-core"
  },
  {
    "package": "fonts-noto-ui-core"
  },
  {
    "package": "fonts-noto-color-emoji"
  }
```

## First successful run

Now supertuxkart starts and is ready to use.


## Creating a session config

To have a nice icon on the desktop, we need to create a session config and script.

Edit data/config/sessions.param
```xml
<sessions>
	<supertuxkart%>
        <name>
            value=<SuperTuxKart>
        </name>
        <icon>
            value=<supertuxkart>
        </icon>
        <run_only_once>
            value=<true>
        </run_only_once>
        extends_base=<sessions.base%>
	</supertuxkart%>
	<supertuxkart0>
	</supertuxkart0>
</sessions>
```

Edit input/all/config/sessions/supertuxkart.py
```python
#!/usr/bin/env python3

import subprocess

command=['/services/supertuxkart/usr/games/supertuxkart']
subprocess.run(command)
```

Make the script executable. The linking is not really necessary, but make development easier since most IDEs need the .py file extension for syntax highlighting.

```bash
chmod +x input/all/config/sessions/supertuxkart.py
ln -s supertuxkart.py supertuxkart0
```

## Ready to run

Now we have the minimum needed for the app.

## Fine tuning

Our app has currently no configuration and we do not have a game server.

## Adding app icons

For the display in the app portal we need a nice icon.
We copy it from the supertux package and create a monochrome version using ImageMagick's convert tool. svg format is preferred but supertux does not have it.

```bash
cp igelpkg.output/data_x64/usr/share/icons/hicolor/128x128/apps/supertuxkart.png data/app.png
convert data/app.png -colorspace gray data/monochrome.png
```

## Adding description

From the output of

```bash
dpkg -I igelpkg.tmp/download/supertuxkart_1.1+ds-1build1_amd64.deb
```
we copy and paste the description to data/descriptions/en


## Adding EULA

We add an EULA that the user needs to accept to data/eula/en.



## Exclude docs in app

To keep the app small we exclude the documentation of the debian packages.

debian/install.json
```json
    "excludes": [
      "usr/share/doc",
      "usr/share/man"
    ]
```


## Remove empty files

We can remove all empty files in the igel/folder

## Adding the game server

We add options to enable and set the name of the game server. The node_action will be triggered when a settings changes and restarts the systemd system service supertuxkart-server.

data/config/server.param
```xml
<server>
    <lan-server>
        value=<false>
        type=<bool>
        runtime=<true>
        displayname[en_us]=<Start lan-server>
        tooltip[en_us]=<Start a LAN server (not a playing client).>
    </lan-server>
    <lan-server-name>
        value=<superigel>
        type=<string>
        runtime=<true>
        displayname[en_us]=<Name of the lan-server>
        tooltip[en_us]=<Name of the LAN server (not a playing client).>
    </lan-server-name>
    node_action=</bin/systemctl restart supertuxkart-server>
</server>
```

We need a script that configures the game server which will be called by a systemd service.

Edit input/all/usr/bin/supertuxkart-server.py
```python
#!/usr/bin/env python3

from os import EX_OK, EX_USAGE
import getsetup3
import subprocess

def get_config() -> dict:

    config = {}
    with getsetup3.Getsetup() as gs:
        config = {
            'lan-server': gs.getvalue('app.supertuxkart.server.lan-server'),
            'lan-server-name': gs.getvalue('app.supertuxkart.server.lan-server-name')
        }
    return config


config = get_config()

if config['lan-server'] == 'false':
    raise SystemExit(EX_OK)

command=['/services/supertuxkart/usr/games/supertuxkart']

if not config['lan-server-name']:
    print('Error: lan-server-name not set')
    raise SystemExit(EX_USAGE)

command.append(f'--lan-server={config["lan-server-name"]}')

subprocess.run(command)
```

Make it executable.

```bash
chmod +x input/all/usr/bin/supertuxkart-server.py
```

Add a systemd system service which will be run at system start.
supertuxkart-server.py will run as unprivileged user.

Edit input/all/etc/systemd/system/supertuxkart-server.service
```ini
[Unit]
Description=SuperTuxKart server

[Service]
Type=simple
DynamicUser=yes
ExecStart=/services/supertuxkart/usr/bin/supertuxkart-server.py
```

Enable the systemd system service at boot.

Add this to debian/install.sh
```bash
enable_system_service supertuxkart-server.service
```

## More configuration options

Playing in windowed mode is no fun, we add an option for fullscreen and the difficulty.

Edit data/config/options.param
```xml
<options>
    <windowmode>
        value=<fullscreen>
        type=<string>
        runtime=<true>
        range=<[window]|[fullscreen]>
        range[en_us]=<[Window][Fullscreen]>
        displayname[en_us]=<Window mode>
        tooltip[en_us]=<Use fullscreen or windowed display.>
    </windowmode>
    <difficulty>
        value=<0>
        type=<range>
        runtime=<true>
        range=<[0]|[1]|[2][3]>
        range[en_us]=<[Beginner][Intermediate][Expert][SuperTux]>
        displayname[en_us]=<Difficulty>
    </difficulty>
</options>
```

We need to extend the session script to pass this options.

Edit input/all/config/sessions/supertuxkart.py
```python
#!/usr/bin/env python3

import getsetup3
import subprocess

def get_config() -> dict:

    config = {}
    with getsetup3.Getsetup() as gs:
        config = {
            'windowmode': gs.getvalue('app.supertuxkart.options.windowmode'),
            'difficulty': gs.getvalue('app.supertuxkart.options.difficulty')
        }
    return config


config = get_config()

command=['/services/supertuxkart/usr/games/supertuxkart']

command.append(f'--difficulty={config["difficulty"]}')

if config['windowmode'] != 'window':
    command.append('--fullscreen')

subprocess.run(command)
```


## Creating a systemd user service

Just for fun we add a systemd user service to pop-up a notification at boot.

Edit input/all/etc/systemd/user/supertuxkart.service
```ini
[Unit]
Description=SuperTuxKart

[Service]
Type=oneshot
ExecStart=/bin/bash -c '/usr/bin/igel-notify-send text -i supertuxkart -t SuperTuxKart -m "Tux wants to race against you" --timeout 120'
```

Enable this service. Add the line to debian/install.sh
```
enable_user_service supertuxkart.service
```



## Create ui.json

So that we can do the configuration in the Setup, we define a UI using the Page Description Language (PDL).

Edit data/config/ui.json
```json
{
    "root": {
        "id": "root",
        "childrenIds": [
            "base"
        ]
    },
    "base": {
        "id": "base",
        "parentId": "root",
        "nlsResourceId": "base",
        "title": "SuperTuxKart",
        "childrenIds": [
            "options",
            "server"
        ]
    },
    "options": {
        "id": "options",
        "nlsResourceId": "options",
        "parentId": "base",
        "title": "Options",
        "elements": {
            "0": {
                "paramId": "app.supertuxkart.options.difficulty",
                "type": "generic"
            }
        }
    },
    "server": {
        "id": "server",
        "nlsResourceId": "server",
        "parentId": "base",
        "title": "Server",
        "elements": {
            "0": {
                "paramId": "app.supertuxkart.server.lan-server",
                "type": "generic"
            },
            "1": {
                "paramId": "app.supertuxkart.server.lan-server-name",
                "type": "generic"
            }
        }
    }
}
```

## Create translation.json

So that the configuration can be displayed in different languages in the Setup, we use the nlsResourceId for reference.

Edit data/config/translation.json
```json
{
    "base": {
        "de": "SuperTuxKart",
        "en": "SuperTuxKart",
        "es": "SuperTuxKart",
        "fr": "SuperTuxKart",
        "it": "SuperTuxKart"
    },
    "options": {
        "de": "Optionen",
        "en": "Options",
        "es": "Opciones",
        "fr": "Options",
        "it": "Opzioni"
    },
    "server": {
        "de": "Server",
        "en": "Server",
        "es": "Servidor",
        "fr": "Serveur",
        "it": "Server"
    }
}
```

## Creating a persistent data partition

You may notice that all highscores are lost after reboot. Let's create a persistent data store to keep the configuration and highscores.

Edit app.json and add
```json
"rw_partition": {
    "size": "small",
    "mountpoint": "/userhome/.config/supertuxkart",
    "flags": [
      "compressed"
    ],
    "post_mount": "chown user /userhome/.config/supertuxkart"
  },
```

post_mount is needed that the user can write to this partition.


## Customizing the source package

We at IGEL love hedgehogs, so we add a self-created kart model to input/all/usr/share/games/supertuxkart/data/karts/ike/ which will add the kart model to the path of supertuxkart.

