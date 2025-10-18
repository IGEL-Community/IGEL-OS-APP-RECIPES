THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Inductive Automation Vision

Free your operators from manually tracking process data on whiteboards and clipboards by creating dynamic, beautiful, real-time dashboards and control screens with Vision. Use the Vision to quickly build any type of visualization for your industrial organization: HMI, historical trending, and alarming screens, plus charts, graphs, and much more.

## Obtain the Vision tar file

- [Download Ignition](https://inductiveautomation.com/downloads/ignition) - `Ignition - Linux 64-bit zip`

- Run the following script to extract: `visionclientlauncher.tar.gz`

```bash linenums="1"
#!/bin/bash
mkdir tar_extract
cd tar_extract
unzip ../Ignition-linux-x86-64-*.zip lib/core/launch/visionclientlauncher.tar.gz
mv lib/core/launch/visionclientlauncher.tar.gz .
rm -rf lib
```