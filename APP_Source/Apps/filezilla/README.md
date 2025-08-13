THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Download FileZilla

https://filezilla-project.org/download.php?platform=linux64

FileZilla_3.69.3_x86_64-linux-gnu.tar.xz

- Note the version of the file
- Rename file to `FileZilla_x86_64-linux-gnu.tar.xz`

```bash linenums="1"
mv FileZilla_*_x86_64-linux-gnu.tar.xz FileZilla_x86_64-linux-gnu.tar.xz && mkdir fz_tmp && tar xvf FileZilla_x86_64-linux-gnu.tar.xz --directory fz_tmp && cd fz_tmp && chmod -R 755 * && tar cjvf ../FileZilla_x86_64-linux-gnu.tar.bz2 * && cd .. && rm -rf fz_tmp
```