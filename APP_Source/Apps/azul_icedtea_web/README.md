THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Download Azul IcedTea-Web

https://www.azul.com/products/components/icedtea-web/

- Note the version of the file
- Rename file to `azul-icedtea-web.linux.zip`

azul-icedtea-web-1.8.8-28.linux.zip

-----

# [About IcedTea-Web](https://docs.azul.com/core/icedteaweb/introduction)

-----

# Path to javaws and testing app

```bash linenums="1"
pushd .
cd /services/azul_icedtea_web/azul-icedtea-web-*
eval JAVAWS_PATH=$(pwd)
export PATH=$JAVAWS_PATH/bin:$PATH
popd
wget https://docs.oracle.com/javase/tutorialJWS/samples/deployment/NotepadJWSProject/Notepad.jnlp
javaws Notepad.jnlp
```

