THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [AWS Client VPN for Linux](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/client-vpn-connect-linux.html)

## Need to obtain the installer

**NOTE:** Obtain the installer file from script below and rename to `awsvpnclient_amd64.deb`

awsvpnclient_5.3.1_amd64.deb

-----

-----

## Need to obtain the client VPN endpoint configuration file

**NOTE:** Follow the link below to obtain client VPN endpoint configuration file.

https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-working-endpoint-export.html

**NOTE:** Zip `.ovpn` file into `ovpn.zip`

-----

-----

- Script to run on Ubuntu 20.04

```bash
#!/bin/bash
#set -x
#trap read debug

# Download AWS VPN Client

sudo apt install curl -y
sudo apt install unzip -y

# https://docs.aws.amazon.com/vpn/latest/clientvpn-user/client-vpn-connect-linux.html
sudo curl https://d20adtppz83p9s.cloudfront.net/GTK/latest/debian-repo/awsvpnclient_public_key.asc | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] https://d20adtppz83p9s.cloudfront.net/GTK/latest/debian-repo ubuntu-20.04 main" > /etc/apt/sources.list.d/aws-vpn-client.list'
sudo apt-get update

MISSING_LIBS="awsvpnclient"

for lib in $MISSING_LIBS; do
  apt-get download $lib
done
```