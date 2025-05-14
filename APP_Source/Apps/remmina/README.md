THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**Note:**

https://remmina.org/

- Obtain Remmina tar.bz2 file by running the following script on Ubuntu 20.04

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

# Build package
APP="remmina"
ZIP_FILE="Remmina"
CLEAN="TRUE"
OS12_CLEAN="12.6.0"
GETVERSION_FILE="../../remmina_*.deb"
MISSING_LIBS="i965-va-driver intel-media-va-driver libaom0 libavahi-ui-gtk3-0 libavcodec58 libavutil56 libayatana-appindicator3-1 libayatana-indicator3-7 libcodec2-0.9 libfreerdp-client2-2 libfreerdp2-2 libgsm1 libigdgmm11 libshine3 libsnappy1v5 libswresample3 libva-drm2 libva-x11-2 libva2 libvdpau1 libvncclient1 libwebp6 libwinpr2-2 libx264-155 libx265-179 libxvidcore4 libzvbi-common libzvbi0 mesa-va-drivers mesa-vdpau-drivers ocl-icd-libopencl1 remmina remmina-common remmina-plugin-rdp remmina-plugin-secret remmina-plugin-vnc va-driver-all vdpau-driver-all libssh-4 libicu66 libvpx6"

# Remmina - add - repository
sudo apt-add-repository ppa:remmina-ppa-team/remmina-next -y
# Remmina - add - repository

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