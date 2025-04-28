THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**Note:**

- Obtain Thunderbird for Linux (Linux version) 64bit and zip it up. Use name `thunderbird.tar.bz2`

https://www.thunderbird.net/en-US/download

- Thunderbird changed package format from tar.bz2 to tar.xz. Currently, IGEL App Creator Portal does not support tar.xz format. Until this is fixed, you must uncompress and re-compress the file:

```bash linenums="1"
mkdir tb_tmp && tar xvf thunderbird.tar.xz --directory tb_tmp && cd tb_tmp && tar cjvf ../thunderbird.tar.bz2 thunderbird && cd .. && rm -rf tb_tmp
```
