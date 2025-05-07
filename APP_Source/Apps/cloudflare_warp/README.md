THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


**NOTE:**

https://developers.cloudflare.com/cloudflare-one/connections/connect-devices/warp/

https://developers.cloudflare.com/cloudflare-one/connections/connect-devices/warp/set-up-warp/

https://developers.cloudflare.com/cloudflare-one/connections/connect-devices/user-side-certificates/manual-deployment/#linux

https://kb.igel.com/en/universal-management-suite/12.07.100/upload-and-assign-files-in-the-igel-ums-web-app

https://developers.cloudflare.com/cloudflare-one/connections/connect-devices/warp/download-warp/#linux

https://developers.cloudflare.com/cloudflare-one/connections/connect-devices/warp/deployment/manual-deployment/

https://developers.cloudflare.com/cloudflare-one/connections/connect-devices/warp/deployment/manual-deployment/#enroll-using-the-cli

-----

https://pkg.cloudflareclient.com/#ubuntu

- Run the following script on Linux system to download Linux installer and rename file to be `cloudflare-warp_amd64.deb`

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

# Add cloudflare gpg key
curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg

# Add this repo to your apt repositories
echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ focal main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list

# Download cloudflare-warp
sudo apt-get update && apt-get download cloudflare-warp
mv cloudflare-warp_*.deb cloudflare-warp_amd64.deb
```

-----

- Connect the client to your organization's Cloudflare Zero Trust instance

https://developers.cloudflare.com/cloudflare-one/connections/connect-devices/warp/deployment/manual-deployment/