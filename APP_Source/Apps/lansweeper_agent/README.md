THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


**NOTE:**

- Edit the builder and change the key for your environment LANSWEEPER_AUTHENTICATION_KEY="4c2db649-014a-41f5-a01d-08950d7af"

- Installing LsAgent on a Linux computer provides details on how to obtain key

- The key can be found in /services/lansweeper_agent/opt/LansweeperAgent/LsAgent.ini as AgentKey=4c2db649-014a-41f5-a01d-08950d7af

## Need to create tar file from installer.

Steps:

- Create Ubuntu VM
- Download the the installer into $HOME/Downloads folder and run the following builder script to create lansweeper_agent.tar.bz2

``` bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

# Creating an IGELOS CP
## Development machine Ubuntu 
ZIP_FILE="Lansweeper_Agent"
LANSWEEPER_AUTHENTICATION_KEY="4c2db649-014a-41f5-a01d-08950d7af"
GETVERSION_FILE="$HOME/Downloads/LsAgent-linux-*.run"

if ! compgen -G "${GETVERSION_FILE}" > /dev/null; then
  echo "***********"
  echo "Obtain Lansweeper Agent (Linux version) 64bit, save into $HOME/Downloads and re-run this script "
  echo "https://www.lansweeper.com/download/lsagent"
  echo "***********"
  exit 1
fi

mkdir build_tar
cd build_tar

#START setup
# file listing before install
pushd .
cd /
#sudo sh -c 'find bin etc home lib opt sbin usr var | sort > /tmp/find_root_listing1.txt'
sudo sh -c 'find etc opt | sort > /tmp/find_root_listing1.txt'
popd

# do install
chmod a+x ${GETVERSION_FILE}
sudo ${GETVERSION_FILE} --agentkey ${LANSWEEPER_AUTHENTICATION_KEY} --mode unattended

# file listing after install
pushd .
cd /
#sudo sh -c 'find bin etc home lib opt sbin usr var | sort > /tmp/find_root_listing2.txt'
sudo sh -c 'find etc opt | sort > /tmp/find_root_listing2.txt'
popd

# tar file of the new files
pushd .
cd /
sudo sh -c 'comm -1 -3 /tmp/find_root_listing1.txt /tmp/find_root_listing2.txt | xargs tar -cjvf /tmp/newfiles.tar.bz2'
popd

cp /tmp/newfiles.tar.bz2 ../lansweeper_agent.tar.bz2
cd ..
rm -rf build_tar
```