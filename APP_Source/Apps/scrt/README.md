THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [VanDyke Software - SecureCRT client for Linux](https://www.vandyke.com/cgi-bin/releases.php?product=securecrt&ver=9.5)

- Download `Ubuntu 20.04 LTS 64-bit` and save as `scrt.ubuntu20-64.x86_64.deb`

- Tested with `scrt-9.5.2-3325.ubuntu20-64.x86_64.deb`

## Run the following commands to download missing libs

```bash linenums="1"
wget -O libicu66.deb \
  https://archive.ubuntu.com/ubuntu/pool/main/i/icu/libicu66_66.1-2ubuntu2.1_amd64.deb

wget -O libssl1.1.deb \
  https://security.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb
```