THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


**NOTE:**

Need to create SAP GUI tar file from installer.

Steps:

- Create Ubuntu VM
- Download the SAP GUI installer into $HOME/Downloads folder and run the following builder script to create sapgui.tar.bz2

```
#!/bin/bash
#set -x
#trap read debug

# Creating an tar file of SAP GUI
## Development machine Ubuntu (OS11 = 22.04; OS12 = 20.04)
CP="sapgui"
ZIP_LOC="https://github.com/IGEL-Community/IGEL-Custom-Partitions/raw/master/CP_Packages/Apps"
ZIP_FILE="SAP_GUI"
FIX_MIME="TRUE"
CLEAN="FALSE"
OS11_CLEAN="11.10.190"
OS12_CLEAN="12.5.1"
USERHOME_FOLDERS="TRUE"
USERHOME_FOLDERS_DIRS=("custom/${CP}/userhome/.SAPGUI")
APPARMOR="FALSE"
#ls -d opt/SAPClients/SAPGUI[0-9]* | cut -c 22-
GETVERSION_FILE="$HOME/Downloads/PlatinGUI-Linux-x86_64-Installation"
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
  echo "Not a valid Ubuntu OS release. OS11 needs 18.04 (bionic) and OS12 needs 20.04 (focal)."
  exit 1
fi

if ! compgen -G "${GETVERSION_FILE}" > /dev/null; then
  echo "***********"
  echo "Obtain SAP GUI ${GETVERSION_FILE} for Linux (Linux version) 64bit, save into $HOME/Downloads and re-run this script "
  echo "https://accounts.sap.com/saml2/idp/sso"
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

find . -name "*.deb" | while read LINE
do
  dpkg -x "${LINE}" custom/${CP}
done

#START setup
# file listing before install
pushd .
cd /
#sudo sh -c 'find bin etc home lib opt sbin usr var | sort > /tmp/find_root_listing1.txt'
sudo sh -c 'find etc opt usr | sort > /tmp/find_root_listing1.txt'
popd

# do install
echo "==============================================="
echo "==============================================="
echo "Installer will run and do not change defaults"
echo "/custom/${CP}/opt/device-service" 
echo "==============================================="
echo "==============================================="
echo ""
read -p "(Press Enter)" name
chmod a+x ${GETVERSION_FILE}
sudo ${GETVERSION_FILE} install -f -s

# file listing after install
pushd .
cd /
#sudo sh -c 'find bin etc home lib opt sbin usr var | sort > /tmp/find_root_listing2.txt'
sudo sh -c 'find etc opt usr | sort > /tmp/find_root_listing2.txt'
popd

# tar file of the new files
pushd .
cd /
sudo sh -c 'comm -1 -3 /tmp/find_root_listing1.txt /tmp/find_root_listing2.txt | xargs tar -cjvf /tmp/newfiles.tar.bz2'
popd

cp /tmp/newfiles.tar.bz2 ../sapgui.tar.bz2
cd ..
rm -rf buld_tar
```