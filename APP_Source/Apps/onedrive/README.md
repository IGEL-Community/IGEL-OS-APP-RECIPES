THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


**NOTE:**

- [OneDrive Client for Linux](https://abraunegg.github.io/)

- [Usage of OneDrive Client for Linux](https://github.com/abraunegg/onedrive/blob/master/docs/usage.md)

- Test app by synchronizing only one folder as noted in [Performing a selective synchronisation via 'sync_list' file](https://github.com/abraunegg/onedrive/blob/master/docs/usage.md#performing-a-selective-synchronisation-via-sync_list-file)

- Run the following script on Linux system to compile latest version of OneDrive for Linux.

```bash linenums="1"
#!/bin/bash
set -x
#trap read debug

# Compile latest OneDrive Client for Linux
# https://abraunegg.github.io/
# https://github.com/abraunegg/onedrive
# https://github.com/abraunegg/onedrive/blob/master/docs/INSTALL.md
## Development machine (Ubuntu 20.04)

sudo apt install unzip -y

sudo apt install -y build-essential libcurl4-openssl-dev libsqlite3-dev pkg-config git curl libnotify-dev libdbus-1-dev
curl -fsS https://dlang.org/install.sh | bash -s dmd
source ~/dlang/dmd-*/activate

mkdir -p build_tar/compile
cd build_tar/compile

git clone https://github.com/abraunegg/onedrive.git
cd onedrive
# change default folders in ~/ to read / write folders in /services_rw/onedrive/userhome
#sed -i 's|~/.config/onedrive|/services_rw/onedrive/userhome/.config/onedrive|g' src/config.d
#sed -i 's|~/OneDrive|/services_rw/onedrive/userhome/OneDrive|g' src/config.d
./configure
make clean
make
#sudo make install

cd ../..

mkdir -p onedrive/usr/local/bin
mkdir -p onedrive/usr/local/onedrive
mkdir -p onedrive/usr/local/etc/logrotate.d
mkdir -p onedrive/lib/systemd/system
mkdir -p onedrive/usr/lib/systemd/user

cp compile/onedrive/onedrive onedrive/usr/local/bin
chmod 0755 onedrive/usr/local/bin/onedrive
cp compile/onedrive/config onedrive/usr/local/onedrive/config
chmod 0644 onedrive/usr/local/onedrive/config
cp compile/onedrive/contrib/logrotate/onedrive.logrotate onedrive/usr/local/etc/logrotate.d/onedrive
chmod 0644 onedrive/usr/local/etc/logrotate.d/onedrive
cp compile/onedrive/contrib/systemd/onedrive@.service onedrive/lib/systemd/system
chmod 0644 onedrive/lib/systemd/system/onedrive@.service
cp compile/onedrive/contrib/systemd/onedrive.service onedrive/usr/lib/systemd/user
chmod 0644 onedrive/usr/lib/systemd/user/onedrive.service

cd onedrive

# create tar.bz2 file
tar cvjf ../../onedrive.tar.bz2 *

cd ../..
rm -rf build_tar
```

-----

-----

## CONFIGURATION

To copy the default config file into user home directory `/userhome/.config/onedrive`

```bash linenums="1"
wget https://raw.githubusercontent.com/abraunegg/onedrive/master/config -O /userhome/.config/onedrive
```

For the supported options see the usage link above for list of  command  line  options for the availability of a configuration key.

Pattern  are  case  insensitive.  * and ? wildcards characters are supported.  Use | to separate multiple patterns. After changing the filters (skip_file or skip_dir in your configs)  you must execute onedrive --synchronize --resync.

## FIRST RUN

After installing the application you must run it at least once from the terminal to authorize it.

```bash linenums="1"
/services/onedrive/usr/local/bin/onedrive
  ```

You will be asked to open a specific link using your web browser  where you  will have to login into your Microsoft Account and give the application the permission to access your files. After  giving  the  permission, you will be redirected to a blank page. Copy the URI of the blank page into the application.

## Performing a selective sync via 'sync_list' file

[Selective sync](https://github.com/abraunegg/onedrive/blob/master/docs/usage.md#performing-a-selective-synchronisation-via-sync_list-file) allows you to sync only specific files and directories. To enable selective sync create a file named `sync_list` in your application configuration directory (default is `/userhome/.config/onedrive`. Each line of the file represents a relative path from your `sync_dir`. All files and directories not matching any line of the file will be skipped during all operations.

```bash linenums="1"
# sync_list supports comments
#
# The ordering of entries is highly recommended - exclusions before inclusions
#
# Exclude temp folder(s) or file(s) under Documents folder(s), anywhere in OneDrive
#!Documents/temp*
#
# Exclude secret data folder in root directory only
#!/Secret_data/*
#
# Include everything else in root directory
# - Use 'sync_root_files' or --sync-root-files option
# Do not use /* as this will include everything including items you are expecting to be excluded
#
# Include my Backup folder(s) or file(s) anywhere on OneDrive
#Backup
#
# Include my Backup folder in root
#/Backup/
#
# Include IGEL folder in root
#/igel-files/
#
```

## Testing your configuration

You are able to [test your configuration](https://github.com/abraunegg/onedrive/blob/master/docs/usage.md#testing-your-configuration) by utilising the `--dry-run` CLI option. No files will be downloaded, uploaded or removed, however the application will display what 'would' have occurred. For example:

```bash linenums="1"
/services/onedrive/usr/local/bin/onedrive --synchronize --verbose --dry-run
```

## SYSTEMD INTEGRATION

**NOTE:** This is configured into the profile to enable and start onedrive service.

Service files are installed into user and system directories.

### OneDrive service running as root user

To enable this mode, run as root user

```
systemctl enable onedrive
systemctl start onedrive
  ```

### OneDrive service running as root user for a non-root user

This mode allows starting  the  OneDrive  service  automatically with system start for multiple users. For each <username> run:

```
systemctl enable onedrive@<username>
systemctl start onedrive@<username>
  ```

### OneDrive service running as non-root user

In  this mode the service will be started when the user logs in. Run as user

```
systemctl --user enable onedrive
systemctl --user start onedrive
  ```

## LOGGING OUTPUT

When running onedrive all actions can be logged to a separate log file. This  can  be  enabled by using the --enable-logging flag.  By default, log files will be written to /var/log/onedrive.

All logfiles will be in the format  of  %username%.onedrive.log,  where %username% represents the user who ran the client.
