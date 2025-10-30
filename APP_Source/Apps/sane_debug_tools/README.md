THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# SANE Debug Tools

- Download SANE debug tools

```bash linenums="1"
wget https://github.com/IGEL-Community/IGEL-Docs-v02/raw/refs/heads/main/docs/Docs/Scripts/HOWTO-COSMOS-sane.tar.bz2.250721-1.zip
unzip HOWTO-COSMOS-sane.tar.bz2.250721-1.zip
rm HOWTO-COSMOS-sane.tar.bz2.250721-1.zip
```

- scanimage to find scanners

```bash
scanimage -L
```

```bash linenums="1"
device `escl:http://10.0.0.2:80' is a Brother MFC-L2750DW series adf,platen scanner
```

- scanimage to scan image into file igel-image.png

**Note:** replace ` escl:http://10.0.0.2:80` with device reported above

```bash
scanimage -d escl:http://10.0.0.2:80 --format=png --mode Color --resolution 600 > igel-image.png
```

- display image

```bash linenums="1"
gpicview igel-image.png
```