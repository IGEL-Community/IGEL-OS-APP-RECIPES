THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Need to obtain the SentinelOne installer file

SentinelAgent_linux_x86_64.deb

- Rename file to `SentinelAgent_linux.deb`

# Notes on installation

https://support.guardz.com/en/articles/10088053-sentinelone-installation-linux

- Run following command to set token value (as root):

```bash linenums="1"
/opt/sentinelone/bin/sentinelctl management token set <token_value>
```

- Start the agent service (as root):

```bash linenums="1"
/opt/sentinelone/bin/sentinelctl control start
```
