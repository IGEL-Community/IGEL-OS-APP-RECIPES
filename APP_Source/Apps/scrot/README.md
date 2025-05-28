THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

https://idroot.us/scrot-command-line-screen-capture/

- Run the following script on Ubuntu 20.04 system to build `scrot.tar.bz2`

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

# Build package
APP="scrot"
CLEAN="TRUE"
OS12_CLEAN="12.6.0"
MISSING_LIBS="giblib1 libid3tag0 libimlib2 scrot"


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