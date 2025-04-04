THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


**NOTE:**

Need to create LibreOffice tar file from installer.

Steps:

- Create Ubuntu VM
- Create builder script from below, run it, and copy libreoffice.tar.bz2


```bash
#!/bin/bash
#set -x
#trap read debug

## Development machine Ubuntu
APP_DIR="libreoffice"

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

mkdir build_tar
cd build_tar

mkdir -p custom/${APP_DIR}

tar zxvf $HOME/Downloads/LibreOffice_*_Linux_x86-64_deb.tar.gz
LIBREOFFICEDIR="LibreOffice_*_Linux_x86-64_deb/DEBS"
find ${LIBREOFFICEDIR} -type f | while read LINE
do
  dpkg -x "${LINE}" custom/libreoffice
done

tar zxvf $HOME/Downloads/LibreOffice_*_Linux_x86-64_deb_helppack_*.tar.gz
dpkg -x LibreOffice_*_Linux_x86-64_deb_helppack_*/DEBS/lib*.deb custom/libreoffice


cd custom/${APP_DIR}
tar cvjf ../../../libreoffice.tar.bz2 *
cd ../../..
rm -rf build_tar
```
