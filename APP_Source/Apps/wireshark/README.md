THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [Wireshark](https://www.wireshark.org/)

## Setup Custom Command 

- [HOWTO Custom Commands](https://igel-community.github.io/IGEL-Docs-v02/Docs/HOWTO-Custom-Commands/)

- To allow user to run Wireshark, setup the following custom command

```bash
#!/bin/bash
#set -x
#trap read debug

#
# Version:
# Allow Wireshark to run as user
#
# Custom Commands: Desktop: Final Desktop Command
#

ACTION="cc-desktop-3fdc-wireshark"

# Send all stdout/stderr from this script to journald/syslog
exec > >(logger -t "$ACTION") 2>&1

echo "Starting"

if [ -d /services/wireshark ]; then
  echo "Setting up setcap on dumpcap"
  setcap cap_net_raw,cap_net_admin=eip /services/wireshark/usr/bin/dumpcap
else
  echo "Wireshark not installed. Nothing to do"
fi

echo "Finished"

exit 0
