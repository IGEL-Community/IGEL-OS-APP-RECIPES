THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [Claude](https://claude.com/product/overview)

Claude is a family of AI chatbots / language models created by the company Anthropic. It’s similar to tools like ChatGPT, Google Gemini, or Microsoft Copilot.

## [Claude Desktop for Linux](https://github.com/aaddrick/claude-desktop-debian)

This project provides build scripts to run Claude Desktop natively on Linux systems. It repackages the official Windows application for Linux

## Steps to download the latest package files - Ubuntu script

- Save the deb file as: `claude-desktop.deb`

- Run the following script to download the latest package files

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

# Download latest files
## Development machine Ubuntu (OS12 = 20.04)
MISSING_LIBS="claude-desktop"

sudo apt install curl unzip -y

# Add the GPG key
curl -fsSL https://aaddrick.github.io/claude-desktop-debian/KEY.gpg | sudo gpg --dearmor -o /usr/share/keyrings/claude-desktop.gpg

# Add the repository
echo "deb [signed-by=/usr/share/keyrings/claude-desktop.gpg arch=amd64,arm64] https://aaddrick.github.io/claude-desktop-debian stable main" | sudo tee /etc/apt/sources.list.d/claude-desktop.list

sudo apt-get update

for lib in $MISSING_LIBS; do
  apt-get download $lib
done

#claude
mv claude-desktop*.deb claude-desktop.deb
```

-----

## Steps to download the latest package files - Docker

- Save the following as `dockerfile`:

```docker linenums="1"
# Choose a base image
FROM debian:bookworm AS build

# Set a working directory inside the image
WORKDIR /tmp
COPY . .

# Copy deb collection script
COPY get-debs.sh .

# Install dependencies
RUN apt update && apt-get install -y curl gnupg binutils xz-utils | tee -a debug.txt

# run get-debs to collect the deb files
RUN bash ./get-debs.sh | tee -a debug.txt

# copy deb files to out folder
RUN mkdir -p /out
RUN cp -vR * /out/

# copy files out of container
FROM scratch AS export
COPY --from=build /out/ /
```

- Save the following as `get-debs.sh`:

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

MISSING_LIBS="claude-desktop"

apt install curl unzip -y
# Add the GPG key
curl -fsSL https://aaddrick.github.io/claude-desktop-debian/KEY.gpg | gpg --dearmor -o /usr/share/keyrings/claude-desktop.gpg

# Add the repository
echo "deb [signed-by=/usr/share/keyrings/claude-desktop.gpg arch=amd64,arm64] https://aaddrick.github.io/claude-desktop-debian stable main" | tee /etc/apt/sources.list.d/claude-desktop.list

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

- Save the following as `run-docker.sh`:

```bash linenums="1"
#!/bin/bash

mkdir -p artifacts
docker system prune -f
docker buildx build --network host --target export --output type=local,dest=./artifacts .
```
