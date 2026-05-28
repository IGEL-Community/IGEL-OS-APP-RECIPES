THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# 7Zip

- Download latest 7zip (64-bit Linux x86-64) and create `7zip.tar.bz2` with the file `7zzs`

- https://www.7-zip.org/download.html

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

wget -O 7zip.tar.xz https://www.7-zip.org/a/7z2601-linux-x64.tar.xz
tar xf 7zip.tar.xz 7zzs
tar cvjf 7zip.tar.bz2 7zzs
rm -f 7zip.tar.xz 7zzs
```

- [7Zip Web Site](https://www.7-zip.org/)

