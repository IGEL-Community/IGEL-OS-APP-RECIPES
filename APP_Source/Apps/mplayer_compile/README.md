THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [MPlayer](http://www.mplayerhq.hu/design7/news.html)

## Use Docker to compile the latest version of mplayer

Summary of steps:

- Create `dockerfile`
- Create `build-mplayer_compile.sh` to create `mplayer_compile.tar.bz2`

### Save the following as `dockerfile`

```bash linenums="1"
cat << "EOF" > dockerfile
FROM debian:bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        git \
        subversion \
        pkg-config \
        yasm \
        nasm \
        python3 \
        perl \
        wget \
        curl \
        xz-utils \
        bzip2 \
        file \
        patchelf \
        libasound2-dev \
        libpulse-dev \
        libx11-dev \
        libxext-dev \
        libxv-dev \
        libxinerama-dev \
        libxrandr-dev \
        libxss-dev \
        libgl1-mesa-dev \
        libvdpau-dev \
        libva-dev \
        libjpeg62-turbo-dev \
        libpng-dev \
        libfreetype6-dev \
        libfontconfig1-dev \
        libfribidi-dev \
        libdvdread-dev \
        libdvdnav-dev \
        libcdio-paranoia-dev \
        libv4l-dev \
        libmad0-dev \
        libmpg123-dev \
        libogg-dev \
        libvorbis-dev \
        libtheora-dev \
        libspeex-dev \
        libopus-dev \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Get latest MPlayer SVN trunk
RUN svn checkout \
    svn://svn.mplayerhq.hu/mplayer/trunk \
    /build/mplayer

WORKDIR /build/mplayer

# Current MPlayer SVN expects an FFmpeg checkout under ./ffmpeg
RUN git clone --depth 1 \
        https://github.com/FFmpeg/FFmpeg.git \
        ffmpeg && \
    touch ffmpeg/mp_auto_pull

# Configure, compile, and install
RUN ./configure \
        --prefix=/opt/mplayer \
        --confdir=/opt/mplayer/etc/mplayer && \
    make -j"$(nproc)" && \
    make install

# Default to PulseAudio / PipeWire Pulse compatibility
RUN mkdir -p /opt/mplayer/etc/mplayer && \
    printf 'ao=pulse,alsa,sdl:aalib\n' > /opt/mplayer/etc/mplayer/mplayer.conf

# Capture build metadata
RUN mkdir -p /opt/mplayer/build-info && \
    svn info > /opt/mplayer/build-info/mplayer-svn-info.txt && \
    git -C ffmpeg rev-parse HEAD > /opt/mplayer/build-info/ffmpeg-git-commit.txt && \
    /opt/mplayer/bin/mplayer -version > /opt/mplayer/build-info/mplayer-version.txt 2>&1 || true

# Capture linked libraries
RUN ldd /opt/mplayer/bin/mplayer > /opt/mplayer/build-info/mplayer-ldd.txt || true

CMD ["/bin/bash"]
EOF
```

### Save the following as `build-mplayer_compile.sh`

```bash linenums="1"
cat << "EOF" > build-mplayer_compile.sh
#!/bin/bash

set -e

IMAGE_NAME="mplayer-bookworm-builder"
CONTAINER_NAME="mplayer-bookworm-export"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/output"

echo "=========================================="
echo " MPlayer Debian Bookworm Builder"
echo "=========================================="

rm -rf "${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}"

docker system prune -f

echo
echo "[1/3] Building Docker image..."
docker build \
    --network host \
    --no-cache \
    -t "${IMAGE_NAME}" \
    "${SCRIPT_DIR}"

echo
echo "[2/3] Creating temporary container..."

docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

docker create \
    --network host \
    --name "${CONTAINER_NAME}" \
    "${IMAGE_NAME}" >/dev/null

echo
echo "[3/3] Copying MPlayer build..."

docker cp \
    "${CONTAINER_NAME}:/opt/mplayer/." \
    "${OUTPUT_DIR}/"

docker rm "${CONTAINER_NAME}" >/dev/null

echo
echo "=========================================="
echo " Build complete"
echo "=========================================="
echo
echo "Output:"
echo "  ${OUTPUT_DIR}"
echo
echo "MPlayer:"
echo "  ${OUTPUT_DIR}/bin/mplayer"
echo
echo "MEncoder:"
echo "  ${OUTPUT_DIR}/bin/mencoder"
echo

if [ -f "${OUTPUT_DIR}/build-info/mplayer-version.txt" ]; then
    echo "MPlayer version:"
    cat "${OUTPUT_DIR}/build-info/mplayer-version.txt"
fi

echo
if [ -f "${OUTPUT_DIR}/build-info/mplayer-svn-info.txt" ]; then
    echo "MPlayer SVN information:"
    grep -E '^(URL|Revision|Last Changed Rev|Last Changed Date):' \
        "${OUTPUT_DIR}/build-info/mplayer-svn-info.txt" || true
fi

echo
if [ -f "${OUTPUT_DIR}/build-info/ffmpeg-git-commit.txt" ]; then
    echo "FFmpeg Git commit:"
    cat "${OUTPUT_DIR}/build-info/ffmpeg-git-commit.txt"
fi

echo
echo "Linked libraries:"
if [ -f "${OUTPUT_DIR}/build-info/mplayer-ldd.txt" ]; then
    cat "${OUTPUT_DIR}/build-info/mplayer-ldd.txt"
fi

echo
echo "Creating mplayer_compile.tar.bz2"
mkdir ${OUTPUT_DIR}/usr
mv ${OUTPUT_DIR}/bin ${OUTPUT_DIR}/usr
pushd .
cd ${OUTPUT_DIR}
tar cvjf mplayer_compile.tar.bz2 usr etc
popd
EOF
chmod a+x build-mplayer_compile.sh
```