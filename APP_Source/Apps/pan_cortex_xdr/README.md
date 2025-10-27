THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Palo Alto Networks Cortex XDR Collector

- Rename collector-VERSION.deb to `collector.deb`

- Obtain `collector.conf` file with the following settings:

```bash
--dist-id YOUR-DIST_ID
--elb-addr https://distributions.traps.paloaltonetworks.com/
```

- Version tested with: collector-1.5.1.1950.deb

-----

## Cortex XDR Collector Installation

### Configuration

The package will copy `collector.conf` into `/etc/panw/` directory.

### Installation

For complete installation instructions including setting up Cortex XDR GPG public key, please visit the [installation page](https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-pro-admin/get-started-with-cortex-xdr-pro/plan-your-cortex-xdr-deployment.html)
