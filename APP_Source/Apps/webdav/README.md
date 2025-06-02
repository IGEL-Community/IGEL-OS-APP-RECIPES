THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Need to obtain the WedDAV installer

https://github.com/hacdias/webdav

https://github.com/hacdias/webdav/releases

Find latest version of linux-amd64-webdav.tar.gz

-----

# Create /opt/webdav/settings/webdav.yml

- Create and provide settings for your environment

https://github.com/hacdias/webdav?tab=readme-ov-file#configuration

# IGEL Distributed App Repository

- [How to Use Distributed App Repositories in IGEL UMS](https://kb.igel.com/en/universal-management-suite/current/how-to-use-distributed-app-repositories-in-igel-um)

- WebDAV files location: `/opt/webdav/files`

-----

# Update app.json to change the file system size for /opt/webdav/files

**NOTE:** This will fail to create partition if not enough disk space

- The example below will create a `5GB` partition

```json linenums="1"
"rw_partition": {
  "size": 5000000
},
```
