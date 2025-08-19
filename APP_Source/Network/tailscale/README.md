THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [Tailscale quickstart](https://tailscale.com/kb/1017/install)

# Obtain the latest app

- Run the following script to obtain latest app:

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

#https://tailscale.com/kb/1039/install-ubuntu-2004

sudo apt install curl -y
sudo apt install unzip -y

sudo curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
sudo curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list

sudo apt-get update

MISSING_LIBS="tailscale"

mkdir build_tar
cd build_tar

for lib in $MISSING_LIBS; do
  apt-get download $lib
done

mv tailscale_*.deb ../tailscale.deb
cd ..
rm -rf build_tar
```

-----

-----

# Connect your machine to your Tailscale network and authenticate in your browser:

- As root:

```bash linenums="1"
tailscale up
```

- find your Tailscale IPv4 address by running:

```bash linenums="1"
tailscale ip -4
```