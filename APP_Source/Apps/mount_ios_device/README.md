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

-----

## Create a python script mount.py to auto mount

- mount.py

```python linenums="1"
import pyudev
import subprocess
import time

APPLE_VENDOR_ID = "05ac"

PAIR_COMMAND = [
    "/dev/.mnt-system/ro/services/mount_ios_devices/usr/bin/devicepair",
    "pair"
]

def pair_device():
    print("Apple device detected! Attempting pairing...")

    while True:
        try:
            subprocess.run(PAIR_COMMAND, check=True)
            print(":white_check_mark: Pairing successful.")
            return True
        except subprocess.CalledProcessError as e:
            print(f":x: Pairing failed, retrying in 2 seconds... ({e})")
            time.sleep(2)

def main():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('usb')

    already_detected = set()

    print("Listening for Apple device connections...")

    for device in iter(monitor.poll, None):
        vendor_id = device.get('ID_VENDOR_ID')

        if vendor_id == APPLE_VENDOR_ID:
            device_id = device.get('DEVPATH')

            if device.action == 'add' and device_id not in already_detected:
                success = pair_device()
                if success:
                    already_detected.add(device_id)

            elif device.action == 'remove' and device_id in already_detected:
                already_detected.remove(device_id)
                print("Apple device disconnected.")

if __name__ == "__main__":
    main()
```

- Import and assign the devices with mount.py

- Create a base profile

System>System Customization>Base

Such as "Final initialization command"

`python3 /wfs/mount.py`

- Restart the device and it should now be able to mount the IOS devices automatically.

**Note:** you need to use the citrix control bar and click on devices and then click on your IPHONE to make it appear into the citrix session. 