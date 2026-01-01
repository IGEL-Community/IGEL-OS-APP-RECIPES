THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [Docker](https://www.docker.com/)

**Note:** Need to run docker as `root`.

## Test Docker with hello-world

```bash linenums="1"
docker run hello-world
```
What happens internally:

- Docker checks if the hello-world image exists locally
- If not, it pulls it from Docker Hub
- Docker creates and runs a container
- The container prints a message and exits

## Docker Examples

- Setup Debian Bookworm (12)

```bash linenums="1"
docker run --network host -it debian:bookworm bash -c \
"apt-get update && apt-get install -y curl iputils-ping && bash"
```

- Setup Ubuntu 22.04

```bash linenums="1"
docker run --network host -it ubuntu:22.04 bash -c \
"apt-get update && apt-get install -y curl iputils-ping && bash"
```

- List docker images

```bash linenums="1"
docker images
```

- Run debian:bookworm

```bash linenums="1"
docker run --network host -it debian:bookworm
```

- Run ubuntu:22.04

```bash linenums="1"
docker run --network host -it ubuntu:22.04
```

## Sample script to collect latest deb files

- Copy and run the following script on Debian / Ubuntu 

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

MISSING_LIBS="containerd.io docker-buildx-plugin docker-ce docker-ce-cli docker-ce-rootless-extras docker-compose-plugin"

sudo apt install curl -y

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

sudo echo \
"deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/debian \
bookworm stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update

mkdir build_tar
cd build_tar

for lib in $MISSING_LIBS; do
  apt-get download $lib
  ls $lib* >> deb-listing.txt
  mv $lib*.deb $lib.deb
done

mv *.deb ..
mv deb-listing.txt ..
cd ..
rm -rf build_tar
```

## Use Docker to collect latest deb files

- Save the following as `dockerfile`:

```dockerfile
# Choose a base image
FROM debian:bookworm AS build

# Set a working directory inside the image
WORKDIR /tmp
COPY . .

# Copy deb collection script
COPY get-debs.sh .

# Install dependencies
RUN apt update && apt-get install -y curl gnupg

# run get-debs to collect the deb files
RUN bash ./get-debs.sh

# copy deb files to out folder
RUN mkdir -p /out
RUN cp -v *.deb /out/
RUN cp -v deb-listing.txt /out/

# copy files out of container
FROM scratch AS export
COPY --from=build /out/ /
```

- Save the following as `get-debs.sh`:

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

MISSING_LIBS="containerd.io docker-buildx-plugin docker-ce docker-ce-cli docker-ce-rootless-extras docker-compose-plugin"

apt install curl -y

curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
"deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/debian \
bookworm stable" | \
tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update

mkdir build_tar
cd build_tar

for lib in $MISSING_LIBS; do
  apt-get download $lib
  ls $lib* >> deb-listing.txt
  mv $lib*.deb $lib.deb
done

mv *.deb ..
mv deb-listing.txt ..
cd ..
rm -rf build_tar
```

- Run the following command:

```bash linenums="1"
mkdir -p artifacts
docker buildx build --network host --target export --output type=local,dest=./artifacts .
```