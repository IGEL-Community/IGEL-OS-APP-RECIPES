THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# FortiDLP Agent

Download agent fortidlp-agent_VERSION.deb and rename to remove version `fortidlp-agent.deb`

fortidlp-agent_12.4.2.deb

## [FortiDLP Agent Deployment Guide](https://docs.fortinet.com/document/fortidlp-agent/12.4.2/fortidlp-agent-deployment-guide/341635/introduction)

### [Generating FortiDLP Agent enrollment tokens](https://docs.fortinet.com/document/fortidlp-agent/12.4.2/fortidlp-agent-deployment-guide/576521/generating-fortidlp-agent-enrollment-tokens)

- Add enrollment token to you UMS profile - enrollment-token.

### How to enroll the FortiDLP Agent on Linux

- Open a command-line interface with root privileges.

- Run the following command, where <code or path> is either the enrollment code or the enrollment bundle path: jazz-agent enroll -f <code or path>.
- When the enrollment succeeds, the output will look as follows:

```bash
Waiting for enrollment to complete...
Enrollment completed.
You should then restart the device.
```