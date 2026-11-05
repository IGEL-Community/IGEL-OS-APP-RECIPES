THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [HCL BigFix Agent](https://support.bigfix.com/install/besclients-nonwindows.html)

- Download Debian (deb) agent

- Recipe tested with `BESAgent-11.0.5.204-debian10.amd64.deb`

- Rename file to `BESAgent.amd64.deb`

- Obtain actionsite masthead (actionsite.afxm) from your BigFix server. The masthead file for each BigFix Server is downloadable at http://servername:port/masthead/masthead.afxm (example: http://bes.bigfix.com:52311/masthead/masthead.afxm). This file will be placed into `/etc/opt/BESClient/actionsite.afxm`.

- Zip `actionsite.afxm` into `actionsite.afxm.zip`

## bigfix-postinst.sh

This script will:

- Run post install settings

## Debug from Journalctl

```bash linenums="1"
jounalctl -t bigfix_postinst
```

## Logs

- Logs are in folder: `/var/opt/BESCLient/_BESData/_Global/Logs`