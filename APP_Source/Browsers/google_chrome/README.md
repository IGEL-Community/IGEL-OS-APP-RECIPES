THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**Note:**

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