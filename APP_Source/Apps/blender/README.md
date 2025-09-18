THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Download Blender

https://www.blender.org/download/

blender-4.5.3-linux-x64.tar.xz

- Note the version of the file
- Rename file to `blender-linux-x64.tar.x2`

**NOTE:** IGEL App Creator Portal does not support tar.xz format. Until this is fixed, you must uncompress and re-compress the file:


```bash linenums="1"
mv blender-*linux-x64.tar.xz blender-linux-x64.tar.xz && mkdir blender_tmp && tar xvf blender-linux-x64.tar.xz --directory blender_tmp && cd blender_tmp && chmod -R 755 * && tar cjvf ../blender-linux-x64.tar.bz2 * && cd .. && rm -rf blender_tmp
```
