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

## List options for Brother MFC-L2750DW

```bash linenums="1"
scanimage -d escl:http://10.0.0.2:80 --help
```

```man linenums="1"
Options specific to device `escl:http://10.0.0.2:80':
  Scan mode:
    --mode Lineart|Gray|Color [Lineart]
        Selects the scan mode (e.g., lineart, monochrome, or color).
    --resolution 100|200|300|600dpi [100]
        Sets the resolution of the scanned image.
    --source Flatbed|ADF|ADF Duplex [Flatbed]
        Selects the scan source (such as a document-feeder).
  Geometry:
    -l 0..210.481mm [0]
        Top-left x position of scan area.
    -t 0..291.507mm [0]
        Top-left y position of scan area.
    -x 5.41866..215.9mm [215.9]
        Width of scan-area.
    -y 5.41866..296.926mm [296.926]
        Height of scan-area.
  Enhancement:
    --preview[=(yes|no)] [no]
        Request a preview-quality scan.
    --preview-in-gray[=(yes|no)] [no]
        Request that all previews are done in monochrome mode.  On a
        three-pass scanner this cuts down the number of passes to one and on a
        one-pass scanner, it reduces the memory requirements and scan-time of
        the preview.
    --brightness 296278272..32767 (in steps of -462015426) [inactive]
        Controls the brightness of the acquired image.
    --contrast 32612..-422329373 (in steps of 32612) [inactive]
        Controls the contrast of the acquired image.
    --sharpen -468633672..22033 (in steps of 296278272) [inactive]
        Set sharpen value.
    --threshold 32767..-468632528 (in steps of 22033) [inactive]
        Select minimum-brightness to get a white point
```