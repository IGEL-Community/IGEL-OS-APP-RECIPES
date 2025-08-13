THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Download Azul Zulu OpenJDK

https://www.azul.com/downloads/zulu-community/?os=ubuntu&package=jdk-fx

zulu21.44.17-ca-jdk21.0.8-linux_x64.tar.gz

- Note the version of the file
- Rename file to `zulu-jdk-linux_x64.tar.gz`

# Setup JAVA_HOME and PATH

- Update for the version of product

```bash linenums="1"
eval JAVA_HOME=/services/azul_openjdk/zulu21.44.17-ca-fx-jdk21.0.8-linux_x64
PATH=/services/azul_openjdk/zulu21.44.17-ca-fx-jdk21.0.8-linux_x64/bin:$PATH
java --version
```
