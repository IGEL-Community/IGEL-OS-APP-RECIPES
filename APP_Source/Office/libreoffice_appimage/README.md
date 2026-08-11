THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [LibreOffice](https://libreoffice.org)

## [LibreOffice as AppImage](https://www.libreoffice.org/download-other/)

- Download Latest Full

```bash linenums="1"
wget https://appimages.libreitalia.org/LibreOffice-latest.full-x86_64.AppImage
```
- Zip it up

```bash linenums="1"
zip LibreOffice-latest.full-x86_64.AppImage.zip LibreOffice-latest.full-x86_64.AppImage
```

- Get version for app packing

```bash
chmod a+x LibreOffice-latest.full-x86_64.AppImage
./LibreOffice-latest.full-x86_64.AppImage --version
```

```bash
LibreOffice 26.2.5.1 997786b8bfe5fadf793c1218fed3f515ec806f1b
```

- Use verion as: `26.2.5+1.0`
