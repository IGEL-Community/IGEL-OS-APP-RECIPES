THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Simplescreenrecorder

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