THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [OneDrive Client for Linux](https://abraunegg.github.io/)

Steps to create latest app:

- Build latest OneDrive client for Linux (recommend the below docker build method)
- Download latest [OneDrive GUI](https://github.com/bpozdena/OneDriveGUI) client and zip into `OneDriveGUI.AppImage.zip`

-----

-----

## Steps to Configure OneDrive

Since IGEL OS has limited storage, identify the folders that will be synchronized via the file: [sync_list ](https://github.com/abraunegg/onedrive/blob/master/docs/usage.md#performing-a-selective-synchronisation-via-sync_list-file)

Steps:

- Start OneDriveGUI
- Create new OneDrive profile
- Select the following folder to hold the synced files: `/userhome/OneDrive`
- Go into profiles (Person Icon) -> Selective Sync
- Add the folders, such as `/igel-files/`
- Select the arrow to start sync
- Login to your OneDrive account with your email address

-----

-----

## Compile latest OneDrive Client from Docker container

Summary of steps:

- Create `dockerfile`
- Create `build-onedrive.sh` to compile putty
- Run docker to collect the files and save into artifacts folder

### Save the following as `dockerfile`

```bash linenums="1"
cat << "EOF" > dockerfile
# Choose a base image
FROM debian:bookworm AS build

# Set a working directory inside the image
WORKDIR /tmp
COPY . .

# Copy deb collection script
COPY build-onedrive.sh .

# Install dependencies
RUN apt update && apt-get install -y curl gnupg

# run build-onedrive to collect the deb files
RUN bash ./build-onedrive.sh

# copy deb files to out folder
RUN mkdir -p /out
RUN cp -v *.tar.bz2 /out/

# copy files out of container
FROM scratch AS export
COPY --from=build /out/ /
EOF
```

### Save the following as `build-onedrive.sh`

```bash linenums="1"
cat << "EOF" > build-onedrive.sh
#!/bin/bash
set -x
#trap read debug

# Compile latest OneDrive Client for Linux
# https://abraunegg.github.io/
# https://github.com/abraunegg/onedrive
# https://github.com/abraunegg/onedrive/blob/master/docs/INSTALL.md
## Development machine (Ubuntu 20.04)

apt install unzip -y

apt install -y build-essential libcurl4-openssl-dev libsqlite3-dev pkg-config git curl libnotify-dev libdbus-1-dev
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
EOF
```

### Save the following as `run-docker.sh`:

```bash linenums="1"
cat << "EOF" > run-docker.sh
#!/bin/bash
#set -x
#trap read debug

mkdir -p artifacts
docker system prune -f
docker buildx build --network host --target export --output type=local,dest=./artifacts .
EOF
```

-----

-----

## Compile the latest OneDrive Client

- Run the following script on Debian bookworm Linux system to compile latest version of OneDrive for Linux.

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