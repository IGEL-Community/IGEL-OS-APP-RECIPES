THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**Note:**

Need to create Linphone VOIP tar file from APPIMAGE.

-----

Steps:

- Create Ubuntu VM
- Run the following builder script to create linphone.tar.bz2.zip

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

# Creating an IGELOS CP for Linphone
## Development machine (Ubuntu 18.04)

if ! compgen -G "$HOME/Downloads/Linphone-*.AppImage" > /dev/null; then
  echo "***********"
  echo "Obtain latest package, save into $HOME/Downloads and re-run this script "
  echo "https://download.linphone.org/releases/linux/app/"
  exit 1
fi

sudo apt install unzip -y

mkdir build_tar
cd build_tar

mkdir -p custom/linphone

# Final package destination
BASEDIR=$PWD/custom/linphone

APPIMAGE0="$HOME/Downloads/Linphone-*.AppImage"
APPIMAGE="$(basename $HOME/Downloads/Linphone-*.AppImage)"

APPIMAGEVERSION=` echo $APPIMAGE  | cut -d- -f 2 | cut -d. -f 1-3`

# chmod a+x
chmod a+x $APPIMAGE0

# executing AppImage
# Next version?: change to mount -o loop ....
$APPIMAGE0 2>&1 >/dev/null &

# wait for Linphone to start
while [ `ps ax | grep AppRun.wrapped | grep -v grep | wc -l` -lt 1 ]
do
    echo "."
    sleep 1
done

echo "Linphone started, proceding.............."

#where is it mounted under /tmp ?
APPTEMPDIR=`mount | grep Lin | awk '{print $3}'`

# copy it to the CP
(cd $APPTEMPDIR;cp -r -p * $BASEDIR)

# killall instances
killall AppRun.wrapped

# comment one line in usr/share/linphone/linphonerc-factory to disable download messages for the CP
sed -i '/^version_check_url_root.*$/s/^/#/' ${BASEDIR}/usr/share/linphone/linphonerc-factory

# new build process into zip file
cd custom/linphone
tar cvjf ../../linphone.tar.bz2 *
cd ../..
zip linphone.tar.bz2.zip linphone.tar.bz2
mv linphone.tar.bz2.zip ..

cd ..
rm -rf build_tar
```