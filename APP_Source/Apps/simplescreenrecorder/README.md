THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# SimpleScreenRecorder

https://www.maartenbaert.be/simplescreenrecorder/

- Run the following script on Ubuntu 20.04 system to build `simplescreenrecorder.tar.bz2`

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

# Build package
APP="simplescreenrecorder"
CLEAN="TRUE"
OS12_CLEAN="12.7.0"
MISSING_LIBS="i965-va-driver intel-media-va-driver libaacs0 libaom0 libavcodec58 libavformat58 libavutil56 libbdplus0 libbluray2 libchromaprint1 libcodec2-0.9 libdouble-conversion3 libgme0 libgsm1 libigdgmm11 libopenmpt0 libpcre2-16-0 libqt5core5a libqt5dbus5 libqt5gui5 libqt5network5 libqt5svg5 libqt5widgets5 libqt5x11extras5 libshine3 libsnappy1v5 libssh-gcrypt-4 libswresample3 libswscale5 libva-drm2 libva-x11-2 libva2 libvdpau1 libx264-155 libx265-179 libxcb-xinerama0 libxcb-xinput0 libxvidcore4 libzvbi-common libzvbi0 mesa-va-drivers mesa-vdpau-drivers ocl-icd-libopencl1 qt5-gtk-platformtheme qttranslations5-l10n simplescreenrecorder simplescreenrecorder-lib va-driver-all vdpau-driver-all libvpx6 libwebp6"

sudo apt-add-repository ppa:maarten-baert/simplescreenrecorder -y
sudo apt update -y

sudo apt install unzip -y

mkdir build_tar
cd build_tar

for lib in $MISSING_LIBS; do
  apt-get download $lib
done

mkdir -p custom/${APP}

find . -name "*.deb" | while read LINE
do
  dpkg -x "${LINE}" custom/${APP}
done

if [ "${CLEAN}" = "TRUE" ]; then
  echo "+++++++=======  STARTING CLEAN of USR =======+++++++"
  wget https://raw.githubusercontent.com/IGEL-Community/IGEL-Custom-Partitions/master/utils/igelos_usr/clean_cp_usr_lib.sh
  chmod a+x clean_cp_usr_lib.sh
  wget https://raw.githubusercontent.com/IGEL-Community/IGEL-Custom-Partitions/master/utils/igelos_usr/clean_cp_usr_share.sh
  chmod a+x clean_cp_usr_share.sh
  ./clean_cp_usr_lib.sh ${OS12_CLEAN}_usr_lib.txt custom/${APP}/usr/lib
  ./clean_cp_usr_share.sh ${OS12_CLEAN}_usr_share.txt custom/${APP}/usr/share
  echo "+++++++=======  DONE CLEAN of USR =======+++++++"
fi

cd custom/${APP}

# build tar.bz2
tar cvjf ../../../${APP}.tar.bz2 .

cd ../../..
rm -rf build_tar
```

-----

-----

## Settings

- Audio input: Source set to correct input source (may need to adjust)
- Container Audio: MP4 (allows for playback in browser)

-----

-----

## User Docker to build simplescreenrecorder.tar.bz2

Steps:

- Create `dockerfile`
- Create `get-tar.bz2.sh`
- Create `run-docker.sh`
- Run, as root, `run-docker.sh
- The `simplescreenrecorder.tar.bz2` will be in the `artifacts` folder

### Save the following as `dockerfile`

```docker
# Choose a base image
FROM ubuntu:20.04 AS build

# Set a working directory inside the image
WORKDIR /tmp
COPY . .

# Copy tar.bz2 collection script
COPY get-tar.bz2.sh .

# Install dependencies
RUN apt update && apt-get install -y curl gnupg bzip2

# run get-tar.bz2 to collect the tar.bz2 files
RUN bash ./get-tar.bz2.sh | tee -a debug.txt

# copy tar.bz2 files to out folder
RUN mkdir -p /out
RUN cp -v *.tar.bz2 /out/
RUN cp -v debug.txt /out/

# copy files out of container
FROM scratch AS export
COPY --from=build /out/ /
```

### Save the following as `get-tar.bz2.sh`

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

# Build package
APP="simplescreenrecorder"
CLEAN="FALSE"
OS12_CLEAN="12.7.0"
MISSING_LIBS="i965-va-driver intel-media-va-driver libaacs0 libaom0 libavcodec58 libavformat58 libavutil56 libbdplus0 libbluray2 libchromaprint1 libcodec2-0.9 libdouble-conversion3 libgme0 libgsm1 libigdgmm11 libopenmpt0 libpcre2-16-0 libqt5core5a libqt5dbus5 libqt5gui5 libqt5network5 libqt5svg5 libqt5widgets5 libqt5x11extras5 libshine3 libsnappy1v5 libssh-gcrypt-4 libswresample3 libswscale5 libva-drm2 libva-x11-2 libva2 libvdpau1 libx264-155 libx265-179 libxcb-xinerama0 libxcb-xinput0 libxvidcore4 libzvbi-common libzvbi0 mesa-va-drivers mesa-vdpau-drivers ocl-icd-libopencl1 qt5-gtk-platformtheme qttranslations5-l10n simplescreenrecorder simplescreenrecorder-lib va-driver-all vdpau-driver-all libvpx6 libwebp6"

apt-add-repository ppa:maarten-baert/simplescreenrecorder -y 
apt update -y

apt install unzip -y

mkdir build_tar
cd build_tar

for lib in $MISSING_LIBS; do
  apt-get download $lib 
done

mkdir -p custom/${APP}

find . -name "*.deb" | while read LINE
do
  dpkg -x "${LINE}" custom/${APP} 
done

if [ "${CLEAN}" = "TRUE" ]; then
  echo "+++++++=======  STARTING CLEAN of USR =======+++++++" 
  wget https://raw.githubusercontent.com/IGEL-Community/IGEL-Custom-Partitions/master/utils/igelos_usr/clean_cp_usr_lib.sh 
  chmod a+x ../clean_cp_usr_lib.sh 
  wget https://raw.githubusercontent.com/IGEL-Community/IGEL-Custom-Partitions/master/utils/igelos_usr/clean_cp_usr_share.sh 
  chmod a+x ../clean_cp_usr_share.sh 
  ../clean_cp_usr_lib.sh ${OS12_CLEAN}_usr_lib.txt custom/${APP}/usr/lib 
  ../clean_cp_usr_share.sh ${OS12_CLEAN}_usr_share.txt custom/${APP}/usr/share 
  echo "+++++++=======  DONE CLEAN of USR =======+++++++" 
fi

cd custom/${APP}

# build tar.bz2
tar cvjf ../../../${APP}.tar.bz2 . 

cd ../../..
cp $LOG_FILE tar.bz2-listing.txt
rm -rf build_tar
```

### Save the following as `run-docker.sh`

```bash linenums="1"
#!/bin/bash
# set -x
# trap read debug

mkdir -p artifacts
docker system prune -f
docker buildx build --network host --target export --output type=local,dest=./artifacts .
```
