THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**Note:**

# Grafana Alloy

- [Install Grafana Alloy on Linux](https://grafana.com/docs/alloy/latest/set-up/install/linux/)
- [Run Grafana Alloy on Linux](https://grafana.com/docs/alloy/latest/set-up/run/linux/)
- [Configure Grafana Alloy on Linux](https://grafana.com/docs/alloy/latest/configure/linux/)

## Sample script to collect latest Alloy installer

- Copy and run the following script on Ubuntu 20.04 system

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

MISSING_LIBS="alloy"

sudo apt install curl unzip -y
sudo curl https://apt.grafana.com/gpg.key | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] https://apt.grafana.com stable main" >> /etc/apt/sources.list.d/grafana.list'
sudo apt-get update

mkdir build_tar
cd build_tar

for lib in $MISSING_LIBS; do
  apt-get download $lib
done

mv alloy_*.deb ../alloy.deb
cd ..
rm -rf build_tar
```