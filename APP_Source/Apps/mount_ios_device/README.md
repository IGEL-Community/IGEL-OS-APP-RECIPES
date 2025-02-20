THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**Note:**

# Mount iOS Device

https://libimobiledevice.org/

Communicate with iOS devices natively.

Main packages: usbmuxd libimobiledevice6 libimobiledevice-utils ifuse

-----

## Sample script to mount iOS device

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

export LD_LIBRARY_PATH=/services/mount_ios_device/usr/lib/x86_64-linux-gnu

if [ ! -e ~/MYPhone ]; then
  mkdir ~/MyPhone
fi

ifuse ~/MyPhone
```

-----

## Sample script to unmount iOS device

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

fusermount -u ~/MypHone
```

-----

## iOS Photo Files

**Q:** Where are the photos stored?

**A:** They are located in the DCIM folder