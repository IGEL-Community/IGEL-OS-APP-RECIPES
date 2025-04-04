THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

BeyondTrust Bomgar

[Bomgar](https://www.beyondtrust.com) 

Bomgar is a remote support provider that allows support technicians
to remotely connect to end-user systems through firewalls from their
computer or mobile device.

Each Bomgar agent install is customer specific and must be downloaded
from the customer's bomgar appliance or cloud admin console.

Linked into `/userhome/.bomgar-scc-\<custom install ID\> `

Steps:

- Tar bomgar-scc-XXXXXXXX.bin into bomgar-scc.tar.bz2:

```bash linenums="1"
tar cvjf bomgar-scc.tar.bz2 bomgar-scc-XXXXX.bin
```
