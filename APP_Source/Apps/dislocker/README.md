THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [Dislocker](https://github.com/Aorimn/dislocker)

## Description: read/write encrypted BitLocker volumes

- Dislocker has been designed to read BitLocker encrypted partitions under a Linux system. The driver used to read volumes encrypted in Windows system versions of the Vista to 10 and BitLocker-To-Go encrypted partitions, that's USB/FAT32 partitions.

- The software works with driver composed of a library, with multiple binaries using this library. Decrypting the partition, you have to give it a mount point where, once keys are decrypted, a file named dislocker-file appears.  This file is a virtual NTFS partition, so you can mount it as any NTFS partition and then read from or write to it. Writing to the NTFS virtual file will change the underlying BitLocker partition content. To use dislocker-find Ruby is required.

- This tool is useful in cryptography managing and forensics investigations.