THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

BeyondTrust UCI

[BeyondTrust](https://www.beyondtrust.com) 

beyondtrust is a remote support provider that allows support technicians
to remotely connect to end-user systems through firewalls from their
computer or mobile device.

Each beyondtrust agent install is customer specific and must be downloaded
from the customer's beyondtrust appliance or cloud admin console.

Linked into `/userhome/.beyondtrust-scc-\<custom install ID\> `

Steps:

- Tar sra-pin-linux_x86_64-*.bin

```bash linenums="1"
tar cvjf sra-pin-linux_x86_64-*.bin

-----
**NOTE:**

- Need to add logic to `pre_package_commands.sh` allow for in place version updates.

- Currently need to remove old version BEFORE applying new version or delete the InstallTimeStamp.log file
