THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Cisco Secure Client

This is a small guide for the IGEL Cisco Secure Client app.

## User settings

User settings which can be configure in the UI will be stored persistently on the read/write partition (/services_rw/cisco_secure_client/userhome/.vpn/.anyconnect) and should survive reboots.

## Custom Profiles

In order to deploy a custom profile (xml), add it to your UMS as 'Undefined' file and transfer it to your managed devices.

The path, the file is transferred to does not really matter but you have to make sure, the setupd parameter 'Profile directory' (app.cisco_secure_client.config.profile_dir) is set to the same location.

The profile will then be permanently stored on the read/write partition at /services_rw/cisco_secure_client/profile and linked to the Secure Client profile directory (/services/cisco_secure_client/opt/cisco/secureclient/vpn/profile/).

### Files Needed from Client

- cisco-secure-client-linux64-VERSION-predeploy-k9.tar.gz and rename to `cisco-secure-client-linux64-predeploy-k9.tar.gz`
- cisco-secure-client-vpn_VERSION_amd64.deb" and rename to `cisco-secure-client-vpn_amd64.deb`
- cisco-secure-client-dart_VERSION_amd64.deb and rename to `cisco-secure-client-dart_amd64.deb`

**NOTE:** Edit recipe to update version number in file `install.json`

### Files Needed from Client

- cisco-secure-client-linux64-VERSION-predeploy-k9.tar.gz
- cisco-secure-client-vpn_VERSION_amd64.deb"
- cisco-secure-client-dart_VERSION_amd64.deb