THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


**NOTE:**

Need to create LibreOffice tar file from installer.

Steps:

- Create Ubuntu VM
- Create builder script from below, run it, and copy libreoffice.tar.bz2.zip

```bash
#!/bin/bash
#set -x
#trap read debug

# Creating an IGELOS App Package
## Development machine Ubuntu (OS11 = 22.04; OS12 = 20.04)
CP="libreoffice"
USERHOME_FOLDERS_DIRS="custom/libreoffice/userhome/.config/libreoffice custom/libreoffice/userhome/Documents"
GETVERSION_FILE="../../LibreOffice_*/DEBS/libreoffice*-base_*.deb"
MISSING_LIBS_OS11=""
MISSING_LIBS_OS12=""

VERSION_ID=$(grep "^VERSION_ID" /etc/os-release | cut -d "\"" -f 2)

if [ "${VERSION_ID}" = "22.04" ]; then
  MISSING_LIBS="${MISSING_LIBS_OS11}"
  IGELOS_ID="OS11"
elif [ "${VERSION_ID}" = "20.04" ]; then
  MISSING_LIBS="${MISSING_LIBS_OS12}"
  IGELOS_ID="OS12"
else
  echo "Not a valid Ubuntu OS release. OS11 needs 22.04 (jammy) and OS12 needs 20.04 (focal)."
  exit 1
fi

if ! compgen -G "$HOME/Downloads/LibreOffice_*_Linux_x86-64_deb.tar.gz" > /dev/null; then
  echo "***********"
  echo "Obtain latest Linux (64-bit) (deb) package, save into $HOME/Downloads and re-run this script "
  echo "https://www.libreoffice.org/download/download/?type=deb-x86_64"
  echo "***********"
  exit 1
fi
if ! compgen -G "$HOME/Downloads/LibreOffice_*_Linux_x86-64_deb_helppack_*.tar.gz" > /dev/null; then
  echo "***********"
  echo "Help for offline use"
  echo "Obtain latest Linux (64-bit) (deb) package, save into $HOME/Downloads and re-run this script "
  echo "https://www.libreoffice.org/download/download/?type=deb-x86_64"
  echo "***********"
  exit 1
fi

sudo apt install unzip -y

mkdir build_tar
cd build_tar

for lib in $MISSING_LIBS; do
  apt-get download $lib
done

mkdir -p custom/${CP}

tar zxvf $HOME/Downloads/LibreOffice_*_Linux_x86-64_deb.tar.gz
LIBREOFFICEDIR="LibreOffice_*_Linux_x86-64_deb/DEBS"
find ${LIBREOFFICEDIR} -type f | while read LINE
do
  dpkg -x "${LINE}" custom/libreoffice
done

tar zxvf $HOME/Downloads/LibreOffice_*_Linux_x86-64_deb_helppack_*.tar.gz
dpkg -x LibreOffice_*_Linux_x86-64_deb_helppack_*/DEBS/lib*.deb custom/libreoffice


cd custom/${CP}
tar cvjf ../../libreoffice.tar.bz2 *
cd ../..
zip ../libreoffice.tar.bz2.zip libreoffice.tar.bz2
cd ../
rm -rf build_tar
```