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

-----

-----

## Loop Fullscreen PowerPoint file

- Run the following script with the PowerPoint file

```bash linenums="1"
cat << "EOF" > loop-pptx.sh
#!/bin/bash
#set -x
#trap read debug

#
# Sample script to loop a PowerPoint presentation with LibreOffice
#

set -u

APPIMAGE="/services/libreoffice/usr/bin/LibreOffice-latest.full-x86_64.AppImage"
INTERVAL=5
STARTUP_DELAY=5
RESTART_DELAY=2

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <presentation.pptx>"
    exit 1
fi

PPTX="$(realpath "$1")"

if [[ ! -f "$PPTX" ]]; then
    echo "ERROR: File not found: $PPTX"
    exit 1
fi

for CMD in xdotool unzip; do
    if ! command -v "$CMD" >/dev/null 2>&1; then
        echo "ERROR: $CMD is not installed."
        exit 1
    fi
done

SLIDE_COUNT="$(
    unzip -Z1 "$PPTX" 2>/dev/null |
    grep -E '^ppt/slides/slide[0-9]+\.xml$' |
    wc -l
)"

if [[ "$SLIDE_COUNT" -lt 1 ]]; then
    echo "ERROR: Could not determine slide count."
    exit 1
fi

echo "Presentation: $PPTX"
echo "Slides:       $SLIDE_COUNT"
echo "Interval:     $INTERVAL seconds"

while true; do
    echo
    echo "Starting LibreOffice presentation..."
    "$APPIMAGE" --show "$PPTX" &
    LO_PID=$!
    echo "LibreOffice PID: $LO_PID"
    sleep "$STARTUP_DELAY"
    CURRENT_SLIDE=1
    while kill -0 "$LO_PID" 2>/dev/null; do
        sleep "$INTERVAL"
        if ! kill -0 "$LO_PID" 2>/dev/null; then
            break
        fi
        if [[ "$CURRENT_SLIDE" -ge "$SLIDE_COUNT" ]]; then
            echo "Looping back to slide 1"
            xdotool key Home
            CURRENT_SLIDE=1
        else
            xdotool key Right
            CURRENT_SLIDE=$((CURRENT_SLIDE + 1))
            echo "Slide $CURRENT_SLIDE / $SLIDE_COUNT"
        fi
    done
    wait "$LO_PID" 2>/dev/null
    EXIT_CODE=$?
    echo
    echo "LibreOffice exited with code: $EXIT_CODE"
    echo "Restarting presentation in $RESTART_DELAY seconds..."
    #sleep "$RESTART_DELAY"
done
EOF
```
