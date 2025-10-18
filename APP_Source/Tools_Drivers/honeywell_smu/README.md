THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Honeywell SMU

The Honeywell command line Scanner Management Utility (SMU) assists with the staging, deployment, and management of barcode scanners.

The key features of Scanner Management Utility are:

- Firmware updates
- Configuration updates
- Golden image and sending end device model specific commands
- Details of available features and work flows

- Download SMU_64_bit_VERSION.zip and rename to `SMU_64_bit.zip`

# Steps to run SMU

- Open a terminal window and go into `/services/honeywell/smu` folder
- Setup `LD_LIBRARY_PATH`
- Run command to print version `./smu /v`

```bash linenums="1"
cd /services/honeywell_smu
LD_LIBRARY_PATH=/services/honeywell_smu/openssl
./smu /v
```