THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)

**Note:** Need to build latest version of Putty

-----

-----

## Build PuTTY from Ubuntu VM

Steps:

- Create Ubuntu VM
- Run the following builder script to create putty.tar.bz2

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

# Creating an IGELOS App for PuTTY
## Development machine (Ubuntu 20.04)

# Obtain latest package and save into Downloads
# Download Latest App for Linux (Debian)
#https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html
if ! compgen -G "$HOME/Downloads/putty-*.tar.gz" > /dev/null; then
  echo "***********"
  echo "Obtain latest Unix source archive, save into $HOME/Downloads and re-run this script "
  echo "https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html"
  exit 1
fi

sudo apt install -y build-essential git libcurl4-gnutls-dev curl libssl-dev automake autoconf libtool cmake pkg-config libgcrypt20-dev libpng-dev libzip-dev libjansson-dev libzbar-dev libgtk-3-dev
sudo apt-get update

mkdir build_tar
cd build_tar

#compile PuTTY
mkdir putty_build
cd putty_build
tar xvf $HOME/Downloads/putty-*.tar.gz
cd putty-*
cmake .
cmake --build .
PUTTY_FILES="plink pscp psftp psusan puttygen pterm putty pageant"
tar cvf ../../cp-putty.tar ${PUTTY_FILES}
VERSION=$(grep "^#define RELEASE" version.h | cut -d " " -f 3)
cd ../..

mkdir -p custom/putty/usr/bin
tar xvf cp-putty.tar --directory custom/putty/usr/bin
chmod 755 custom/putty/usr/bin/*

# new build process into zip file
cd custom/putty
tar cvjf ../../../putty.tar.bz2 *
cd ../../..
rm -rf build_tar
```

## Build PuTTY from Docker container

Summary of steps:

- Create `dockerfile`
- Create `build-putty.sh` to compile putty
- Download latest Unix source archive putty-VERSION.tar.gz
- Run docker to collect the files and save into artifacts folder

### Save the following as `dockerfile`

```bash linenums="1"
# Choose a base image
FROM debian:bookworm AS build

# Set a working directory inside the image
WORKDIR /tmp
COPY . .

# Copy deb collection script
COPY build-putty.sh .
COPY putty-*.tar.gz .

# Install dependencies
RUN apt update && apt-get install -y curl gnupg

# run build-putty to collect the deb files
RUN bash ./build-putty.sh

# copy deb files to out folder
RUN mkdir -p /out
RUN cp -v *.tar.bz2 /out/

# copy files out of container
FROM scratch AS export
COPY --from=build /out/ /
```

### Save the following as `build-putty.sh`

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

# Creating an IGELOS App for PuTTY
# Obtain latest package and save into Downloads
# Download Latest App for Linux (Debian)
#https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html

apt install -y build-essential git libcurl4-gnutls-dev curl libssl-dev automake autoconf libtool cmake pkg-config libgcrypt20-dev libpng-dev libzip-dev libjansson-dev libzbar-dev libgtk-3-dev
apt-get update

mkdir build_tar
cd build_tar

#compile PuTTY
mkdir putty_build
cd putty_build
echo $pwd
tar xvf ../../putty-*.tar.gz
cd putty-*
echo "in putty dir"
cmake .
cmake --build .
PUTTY_FILES="plink pscp psftp psusan puttygen pterm putty pageant"
tar cvf ../../cp-putty.tar ${PUTTY_FILES}
VERSION=$(grep "^#define RELEASE" version.h | cut -d " " -f 3)
cd ../..

mkdir -p custom/putty/usr/bin
tar xvf cp-putty.tar --directory custom/putty/usr/bin
chmod 755 custom/putty/usr/bin/*

# new build process into zip file
cd custom/putty
tar cvjf ../../../putty.tar.bz2 *
cd ../../..
rm -rf build_tar
```

### Run Docker with the following script:

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

mkdir -p artifacts
docker system prune -f
docker buildx build --network host --target export --output type=local,dest=./artifacts .
```