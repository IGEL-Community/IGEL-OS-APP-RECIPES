THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Tailscale VPN

- Build version tied to Ubuntu 20.04

- [Tailscale Official Website](https://tailscale.com/)

- Zero-configuration VPN that creates a secure WireGuard network between your devices

**NOTE:** After deployment, you'll need to authenticate with Tailscale using the command line.

## Initial Setup

1. Deploy the app through UMS
2. Open a terminal and run: `tailscale up`
3. Follow the authentication URL to connect to your Tailscale network

## Usage

- `tailscale status` - Show current connection status
- `tailscale ip` - Show Tailscale IP addresses
- `tailscale ping [hostname]` - Test connectivity to another device
- `tailscale netcheck` - Diagnose network connectivity

## Configuration

The Tailscale daemon (tailscaled) runs as a system service and starts automatically.

## Building the IGEL App

1. Upload the `tailscale_1.86.2_amd64.deb` file to the IGEL App Creator Portal
2. Upload all files from the `data`, `igel` directories and `app.json`
3. Build and sign the application
4. Deploy through UMS
