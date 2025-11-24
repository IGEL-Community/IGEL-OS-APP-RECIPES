THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# 7Zip

- Currently, IGEL App Creator Portal does not support tar.xz format. Until this is fixed, you must uncompress and re-compress the file:

- Download latest 7zip and create `7zip.tar.bz2`

```bash linenums="1"
wget -O 7zip.tar.xz https://www.7-zip.org/a/7z2501-linux-x64.tar.xz
tar xf 7zip.tar.xz 7zzs
tar cvjf 7zip.tar.bz2 7zzs
rm -f 7zip.tar.xz 7zzs
```

- [7Zip Web Site](https://www.7-zip.org/)

