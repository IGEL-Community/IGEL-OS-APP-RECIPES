THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [Chrome](https://www.google.com/chrome/)

- Run the following script to download the latest package files

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

# Download latest files
## Development machine Ubuntu (OS12 = 20.04)
APP="chrome"
MISSING_LIBS="google-chrome-stable endpoint-verification"

sudo apt install curl unzip -y
sudo curl https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
sudo sh -c 'echo "deb [arch=amd64] http://packages.cloud.google.com/apt endpoint-verification main" >> /etc/apt/sources.list.d/google.list'
sudo apt-get update

for lib in $MISSING_LIBS; do
  apt-get download $lib
done

#endpoint-verification_1718917546900-645149045_amd64.deb
mv endpoint-verification_*_amd64.deb endpoint-verification_amd64.deb

#google-chrome-stable_138.0.7204.49-1_amd64.deb
mv google-chrome-stable_*_amd64.deb google-chrome-stable_amd64.deb
```
# Use Docker to collect deb files

- Save [dockerfile](https://github.com/IGEL-Community/IGEL-OS-APP-RECIPES/tree/main/APP_Source/Apps/docker#use-docker-to-collect-latest-deb-files)

- Save the following as `get-debs.sh`:

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

MISSING_LIBS="google-chrome-stable endpoint-verification"

curl https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
sh -c 'echo "deb [arch=amd64] http://packages.cloud.google.com/apt endpoint-verification main" >> /etc/apt/sources.list.d/google.list'
apt-get update

mkdir build_tar
cd build_tar

for lib in $MISSING_LIBS; do
  apt-get download $lib
  mv $lib*.deb $lib.deb
done

mv *.deb ..
cd ..
rm -rf build_tar
```

- Run the following command:

```bash linenums="1"
mkdir -p artifacts
docker buildx build --network host --target export --output type=local,dest=./artifacts .
```

-----

-----

# How to Chromecast

- Launch Google Chrome and open content to share

- Click on three vertical dots on the right corner of the chrome browser to open up the menu.

- Click on `Cast,save, and share` to start casting the video on the Chromecast device.
