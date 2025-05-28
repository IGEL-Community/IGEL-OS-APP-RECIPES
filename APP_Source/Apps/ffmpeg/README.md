THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

https://ffmpeg.org

https://ourcodeworld.com/articles/read/1435/how-to-convert-a-wav-file-to-mp3-using-ffmpeg

- Run the following script on Ubuntu 20.04 system to build `ffmpeg.tar.bz2`

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

# Build package
APP="ffmpeg"
CLEAN="TRUE"
OS12_CLEAN="12.6.0"
MISSING_LIBS="ffmpeg i965-va-driver intel-media-va-driver libaacs0 libaom0 libass9 libavcodec58 libavdevice58 libavfilter7 libavformat58 libavresample4 libavutil56 libbdplus0 libbluray2 libbs2b0 libchromaprint1 libcodec2-0.9 libdc1394-22 libfftw3-double3 libflite1 libgme0 libgsm1 libigdgmm11 liblilv-0-0 libmysofa1 libnorm1 libopenal-data libopenal1 libopenmpt0 libpgm-5.2-0 libpostproc55 librubberband2 libsdl2-2.0-0 libserd-0-0 libshine3 libsnappy1v5 libsndio7.0 libsord-0-0 libsratom-0-0 libssh-gcrypt-4 libswresample3 libswscale5 libva-drm2 libva-x11-2 libva2 libvdpau1 libvidstab1.1 libx264-155 libx265-179 libxvidcore4 libzmq5 libzvbi-common libzvbi0 mesa-va-drivers mesa-vdpau-drivers ocl-icd-libopencl1 va-driver-all vdpau-driver-all"

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