THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [PCManFM](https://github.com/lxqt/pcmanfm-qt)

## Customization - File Manager Actions

**NOTE:** Place these files in `/userhome/.local/share/file-manager/actions`

- Open a terminal window on a folder: `openterminal.desktop`

```desktop
[Desktop Entry]
Type=Action
Name=Open Terminal Here
Icon=utilities-terminal
Profiles=profile-zero;

[X-Action-Profile profile-zero]
Exec=/usr/bin/xfce4-terminal -T %f --geometry 90x38 --working-directory=%f
```

- Compress folder: `compress.desktop`

```desktop
[Desktop Entry]
Type=Action
Name=Compress to ZIP
Icon=package-x-generic
Profiles=profile-zero;

[X-Action-Profile profile-zero]
MimeTypes=inode/directory;application/x-directory;
Exec=zip -r %f.zip %f
```

- View images: `imageview.desktop`

```desktop
[Desktop Entry]
Type=Action
Name=View Image
Icon=utilities-terminal
Profiles=profile-zero;

[X-Action-Profile profile-zero]
Exec=/usr/bin/gpicview %f
```