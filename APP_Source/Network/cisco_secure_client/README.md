THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Cisco Secure Client

This is a small guide for the IGEL Cisco Secure Client app.

## User settings

User settings which can be configure in the UI will be stored persistently on the read/write partition (/services_rw/cisco_secure_client/userhome/.vpn/.anyconnect) and should survive reboots.

## Custom Profiles

In order to deploy a custom profile (xml), add it to your UMS as 'Undefined' file and transfer it to your managed devices.

The path, the file is transferred to does not really matter but you have to make sure, the setupd parameter 'Profile directory' (app.cisco_secure_client.config.profile_dir) is set to the same location.

The profile will then be permanently stored on the read/write partition at /services_rw/cisco_secure_client/profile and linked to the Secure Client profile directory (/services/cisco_secure_client/opt/cisco/secureclient/vpn/profile/).

## Files Needed from Client

- cisco-secure-client-linux64-VERSION-predeploy-k9.tar.gz and rename to `cisco-secure-client-linux64-predeploy-k9.tar.gz`
- cisco-secure-client-vpn_VERSION_amd64.deb" and rename to `cisco-secure-client-vpn_amd64.deb`
- cisco-secure-client-dart_VERSION_amd64.deb and rename to `cisco-secure-client-dart_amd64.deb`

**NOTE:** Edit recipe to update version number in file `install.json`

-----

-----

## Cisco-Secure-Client-XML-Profile-Template.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<AnyConnectProfile xmlns="http://schemas.xmlsoap.org/encoding/">

  <!-- ========================================================= -->
  <!--        SERVER LIST (WHAT USERS SEE IN THE DROP-DOWN)       -->
  <!-- ========================================================= -->
  <ServerList>
    <HostEntry>
      <HostName>My Corporate VPN</HostName>            <!-- User-friendly name -->
      <HostAddress>vpn.example.com</HostAddress>       <!-- FQDN or IP -->
      <PrimaryProtocol>HTTPS</PrimaryProtocol>         <!-- Usually HTTPS -->
    </HostEntry>

    <!-- Duplicate for more VPN gateways
    <HostEntry>
      <HostName>Backup VPN</HostName>
      <HostAddress>backupvpn.example.com</HostAddress>
    </HostEntry>
    -->
  </ServerList>

  <!-- ========================================================= -->
  <!--                CLIENT BEHAVIOR SETTINGS                    -->
  <!-- ========================================================= -->
  <ClientInitialization>

    <!-- Auto-connect behavior -->
    <AutoConnectOnStart UserControllable="true">false</AutoConnectOnStart>
    <MinimizeOnConnect UserControllable="true">true</MinimizeOnConnect>

    <!-- Allow users to type a hostname manually -->
    <AllowManualHostInput>true</AllowManualHostInput>

    <!-- LAN access on connect -->
    <LocalLanAccess UserControllable="true">false</LocalLanAccess>

    <!-- Certificate lookup on Linux -->
    <CertificateStoreLinux>All</CertificateStoreLinux>
    <!-- Values: "Machine" "User" "All" -->

    <!-- Reconnect after interruption -->
    <AutoReconnect UserControllable="false">true</AutoReconnect>
    <AutoReconnectBehavior>ReconnectAfterResume</AutoReconnectBehavior>

    <!-- Logging -->
    <Logging Level="INFO"/>
  </ClientInitialization>

  <!-- ========================================================= -->
  <!--                     VPN PROTOCOL OPTIONS                   -->
  <!-- ========================================================= -->
  <VPNProtocol>
    <IPProtocolSupport>IPv4,IPv6</IPProtocolSupport>
    <PseudoDefaultGatewayAddress>Override</PseudoDefaultGatewayAddress>
  </VPNProtocol>

  <!-- ========================================================= -->
  <!--                    PROXY BEHAVIOR                          -->
  <!-- ========================================================= -->
  <ProxySettings>
    <ProxyMode>Native</ProxyMode>
    <AllowLocalProxyConnections>true</AllowLocalProxyConnections>
  </ProxySettings>

  <!-- ========================================================= -->
  <!--                  SCRIPTS (Linux compatible)               -->
  <!-- ========================================================= -->
  <Scripting>
    <!-- Place scripts in: /opt/cisco/secureclient/vpn/scripts -->
    <!-- and make executable: chmod +x script.sh -->

    <!-- Example scripts (optional) -->
    <EnableScripting>true</EnableScripting>

    <!-- Uncomment if needed
    <OnConnect>
      <Command>/opt/cisco/secureclient/vpn/scripts/on_connect.sh</Command>
    </OnConnect>

    <OnDisconnect>
      <Command>/opt/cisco/secureclient/vpn/scripts/on_disconnect.sh</Command>
    </OnDisconnect>
    -->
  </Scripting>

  <!-- ========================================================= -->
  <!--                    NETWORK VISIBILITY                      -->
  <!-- ========================================================= -->
  <Preferences>
    <!-- Allow DNS fallback when VPN split DNS is in effect -->
    <AllowLocalDNS>true</AllowLocalDNS>

    <!-- Traffic behavior -->
    <EnableTransportProtocolPreference>true</EnableTransportProtocolPreference>
  </Preferences>

</AnyConnectProfile>
```

-----

-----

## Cisco Secure Client App has no build in mechanism to handle certificates

- Use custom commands

- At least three files are needed (CA certificate, Auth Certificate, Private key).

- Put those files to /wfs/ via Filetransfer

- Use custom commands to create the following directories: 

```bash
/userhome/.cisco/certificates/ca/ 
/userhome/.cisco/certificates/client/ 
/userhome/.cisco/certificates/client/private/
```

- Then use ln -s to link the certs from /wfs/ to those directories. 