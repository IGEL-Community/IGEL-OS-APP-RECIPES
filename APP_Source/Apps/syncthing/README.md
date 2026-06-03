THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [Syncthing](https://syncthing.net)

Syncthing is an application that lets you synchronize your files across multiple devices. This means the creation, modification or deletion of files on one machine will automatically be replicated to your other devices. We believe your data is your data alone and you deserve to choose where it is stored. Therefore Syncthing does not upload your data to the cloud but exchanges your data across your machines as soon as they are online at the same time.

## Steps to download the latest package files - Ubuntu script

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

sudo mkdir -p /etc/apt/keyrings
sudo curl -L -o /etc/apt/keyrings/syncthing-archive-keyring.gpg https://syncthing.net/release-key.gpg
echo "deb [signed-by=/etc/apt/keyrings/syncthing-archive-keyring.gpg] https://apt.syncthing.net/ syncthing stable-v2" | sudo tee /etc/apt/sources.list.d/syncthing.list
sudo apt-get update
apt-get download syncthing
echo "Downloaded" syncthing_*_amd64.deb
mv syncthing_*_amd64.deb syncthing_amd64.deb
```

## Build Syncthing from Docker container

Summary of steps:

- Create `dockerfile`
- Create `get-syncthing.sh` to collect deb file
- Run docker to collect the deb file and save into artifacts folder

### Save the following as `dockerfile`

```bash linenums="1"
# Choose a base image
FROM debian:bookworm AS build

# Set a working directory inside the image
WORKDIR /tmp
COPY . .

# Copy deb collection script
COPY get-syncthing.sh .

# Install dependencies
RUN apt update && apt-get install -y --no-install-recommends ca-certificates curl gnupg 

# run build-putty to collect the deb files
RUN bash ./get-syncthing.sh

# copy deb files to out folder
RUN mkdir -p /out
RUN cp -v *.deb /out/

# copy files out of container
FROM scratch AS export
COPY --from=build /out/ /
```

### Save the following as `get-syncthing.sh`

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

apt-get update
apt-get install -y --no-install-recommends ca-certificates curl gnupg 

mkdir -p /etc/apt/keyrings
curl -L -o /etc/apt/keyrings/syncthing-archive-keyring.gpg https://syncthing.net/release-key.gpg
echo "deb [signed-by=/etc/apt/keyrings/syncthing-archive-keyring.gpg] https://apt.syncthing.net/ syncthing stable-v2" | tee /etc/apt/sources.list.d/syncthing.list
apt-get update
apt-get download syncthing
#mv syncthing_*_amd64.deb syncthing_amd64.deb
```

### Run Docker with the following script:

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

mkdir -p artifacts
docker system prune -f
docker buildx build --network host --target export --output type=local,dest=./artifacts .
```