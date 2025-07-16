THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## MobiControl Agent for Linux

https://pulse.soti.net/support/soti-mobicontrol/agent-downloads/linux/generic-agent/

```
Processor: x64
Device with User Interface: Yes
Agent Version: Select Latest
```

LinuxAgent202511_x64_64bit.tar.gz

**NOTE:**

- Obtain the installer, rename to `LinuxAgent_x64_64bit.tar.gz`
- Obtain the MCSetup.ini file, zip into `MSSetup.zip`

## Vendor Web Site for Support

- [Enroll Linux Device](https://soti.net/mc/help/v14.0/en/console/devices/managing/enrolling/platforms/linux_enroll.html)

-----

-----

## Setup Final Desktop Command

- The installation of MobiControl is not running from systemctl and need to create a final desktop command

- Following the note from [IGEL Community Docs: HOWTO Custom Commands](https://igel-community.github.io/IGEL-Docs-v02/Docs/HOWTO-Custom-Commands/), create final desktop command, `cc-desktop-3fdc-mobicontrol.sh`  with the following content:

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

#
# MobiControl
#
# Custom Commands: Desktop: Final Desktop Command
#

ACTION="cc-desktop-3fdc-mobicontrol"

APP_INIT="/etc/mobicontrol/mobicontrol-init.sh"

# output to systemlog with ID amd tag
LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

if [ -e ${APP_INIT} ]; then
  echo "Running MobiControl Init" | $LOGGER
  /bin/bash ${APP_INIT}
fi

echo "Finished" | $LOGGER

exit 0
```