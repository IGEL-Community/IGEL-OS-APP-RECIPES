THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Value Set

An application that can be used to create IGEL app registry values.

## Sample build script that will inject into these two locations

- Items to inject into:

```text
auth.login.autologin.password
auth.login.autologin.username
```

- Set username:

```bash linenums="1"
/bin/setuservalue auth.login.autologin.username zippy
```

- Set password:

```bash linenums="1"
/bin/setusercryptparam auth.login.autologin.password "the-password"
```

- Get username:

```bash linenums="1"
/bin/get auth.login.autologin.username
```

- Encrypt file credentials.txt into credentials.enc:

```bash linenums="1"
openssl enc -aes-256-cbc -salt -pbkdf2 -in credentials.txt -out credentials.enc
```

- read-enc-file.sh

```bash linenums="1"
cat << "EOF" > read-enc-file.sh
#!/bin/bash
#set -x
#trap read debug

#
# Version:
# Setup auto login:
#
# auth.login.autologin.password
# auth.login.autologin.username
#
# encrypt file credentials.txt
# openssl enc -aes-256-cbc -salt -pbkdf2 -in credentials.txt -out credentials.enc
#
# Custom Commands: Base: Final initialization command
#

ACTION="cc-base-3fic-autologin"

# output to systemlog with ID amd tag
LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

#AUTOLOGIN_FILE="/wfs/autologin-file.enc"
AUTOLOGIN_FILE="credentials.enc"

input_file="${AUTOLOGIN_FILE}"
password='$(bin/get app.valueset.config.value1)'
#password='123456$'

if [[ ! -f "$input_file" ]]; then
    echo "Error: File '$input_file' not found." | $LOGGER
    exit 1
fi

THIS_HOSTNAME=$(hostname)

# Decrypt and process the CSV without writing plaintext to disk
openssl enc -d -aes-256-cbc \
    -pbkdf2 \
    -in "$input_file" \
    -pass pass:"$password" |
tail -n +2 |
while IFS=',' read -r hostname userid userpassword; do
    echo "Hostname : $hostname"
    echo "User ID  : $userid"
    echo "Password : $userpassword"
    echo "----------------------"
    if [ "${THIS_HOSTNAME}" == "$hostname" ]; then
        #echo "Setting user '$userid' and password for autologin" | $LOGGER
        echo "Setting user '$userid' and password for autologin"
        /bin/setuservalue auth.login.autologin.username $userid
        /bin/setusercryptparam auth.login.autologin.password "$userpassword"
    fi
done

echo "Finished" | $LOGGER

exit 0
EOF
chmod a+x read-enc-file.sh
```

- credentials.txt

```bash linenums="1"
cat << "EOF" > credentials.txt
hostname,username,password
host1,name1,password1
host2,name2,password2
host3,name3,password3
host4,name4,password4
ITC10B6762436B2,fubar1,abcdef$
EOF
```

- Command to create credentials.enc

```bash linenums="1"
openssl enc -aes-256-cbc -salt -pbkdf2 -in credentials.txt -out credentials.enc
```