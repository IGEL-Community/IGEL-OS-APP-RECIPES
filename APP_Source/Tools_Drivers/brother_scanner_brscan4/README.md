THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Brother Scanner brscan4

- Scanner driver 64bit (deb package)
- This recipe for version 4. Modify recipe for other versions (1,2,3,5)

**NOTE:**

- Use brsaneconfig (for brscan models), brsaneconfig2 (for brscan2 models), brsaneconfig3 (for brscan3 models), brsaneconfig4 (for brscan4 models) or brsaneconfig5 (for brscan5 models) accordingly.

-----

## Search for version based on model of scanner

- [Find version of brscan](https://support.brother.com/g/b/productsearch.aspx?c=us&lang=en&content=dl)

- Test with version 4 is brscan4-0.4.11-1.amd64.deb
- Rename to `brscan4.amd64.deb`

-----

## Steps to setup scanner

- Add network scanner entry:

```bash linenums="1"
brsaneconfig4 -a name=(name your device) model=(model name) ip=xx.xx.xx.xx
```

- Confirm network scanner entry

```bash linenums="1"
brsaneconfig4 -q | grep (name of your device)
```

- Open a scanner application [simple-scan](https://github.com/IGEL-Community/IGEL-OS-APP-RECIPES/tree/main/APP_Source/Apps/simple_scan) and try a test scan.