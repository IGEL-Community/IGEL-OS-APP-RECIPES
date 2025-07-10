THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**Note:**

https://greenhost.cloud/how-to-configure-webdav-access-with-apache-on-ubuntu-24-04-or-newer/

- The configuration files can be found in `/wfs/apache`

- [Apache Authentication and Authorization](https://httpd.apache.org/docs/2.4/howto/auth.html)

- [htdigest - manage user files for digest authentication](https://httpd.apache.org/docs/2.4/programs/htdigest.html)

- Create digest account for the user `igel`:

```bash linenums="1"
htdigest -c /wfs/apache/.htdigest ums igel
```

## /wfs/apache/webdav.conf

```bash linenums="1"
DocumentRoot /var/www/webdav

Alias /webdav /var/www/webdav

<Directory /var/www/webdav>
    Options Indexes FollowSymLinks
    AllowOverride AuthConfig
    Dav On
    AuthType Digest
    AuthName "ums"
    AuthUserFile "/wfs/apache/.htdigest"
    Reguire user igel
</Directory>
```