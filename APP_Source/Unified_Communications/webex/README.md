THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**Note:**

Obtain Webex for Linux and zip it up. Use name `Webex.deb.zip`

```bash linenums="1"
wget https://binaries.webex.com/WebexDesktop-Ubuntu-Official-Package/Webex.deb
```

-----

- To use Webex over a proxy server, create a script with this content and use for the start of Webex:

```bash linenums="1"
#!/bin/bash
export http_proxy=http://proxy-host:proxy-port
export https_proxy=https://proxy-host:proxy-port
/custom/webex/opt/Webex/bin/CiscoCollabHost --proxy-server=proxy-host:proxy-port
```

