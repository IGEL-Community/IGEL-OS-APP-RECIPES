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

-----

-----

## Notes on Setting up UMS Distributed App Repository

- [IGEL KB: How to Use Distributed App Repositories in IGEL UMS](https://kb.igel.com/en/universal-management-suite/current/how-to-use-distributed-app-repositories-in-igel-um)

-----

-----

## Set permissions after apache2 starts up

```bash linenums="1"
chown -R www-data:www-data /services_rw/apache/var/www/webdav
chown -R 775 /services_rw/apache/var/www/webdav
```

## How to use Curl with WebDAV

- Create a folder

```bash linenums="1"
curl -i --digest -u igel:igel-password -X MKCOL http://igel-device/webdav/testdir
```

- Add a file to a folder

```bash linenums="1"
curl -i --digest -u igel:igel-password -T /etc/os-release http://igel-device/webdav/testdir/os-release
```

- Download a file

```bash linenums="1"
curl -L --digest -u igel:igel-password http://igel-device/webdav/testdir/os-release --output /tmp/os-release
```