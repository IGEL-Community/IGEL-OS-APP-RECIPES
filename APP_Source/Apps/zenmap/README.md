THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [Zenmap](https://nmap.org/zenmap/)

- To run `nmap` as user, add `--privileged`

```bash
nmap --privileged -sS -O IP-Address-to-Check
```

## Setup Custom Command 

- [HOWTO Custom Commands](https://igel-community.github.io/IGEL-Docs-v02/Docs/HOWTO-Custom-Commands/)

- To allow user to run Zenmap, setup the following custom command

```bash
cat << "EOF" > cc-desktop-3fdc-zenmap.sh
#!/bin/bash
#set -x
#trap read debug

#
# Version:
# Allow Zenmap to run as user
#
# Custom Commands: Desktop: Final Desktop Command
#

ACTION="cc-desktop-3fdc-zenmap"

# Send all stdout/stderr from this script to journald/syslog
exec > >(logger -t "$ACTION") 2>&1

echo "Starting"

if [ -d /services/zenmap ]; then
  echo "Setting up setcap on nmap"
  setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip /services/zenmap/usr/local/bin/nmap
else
  echo "Zenmap not installed. Nothing to do"
fi

echo "Finished"

exit 0
EOF
```

## Build Zenmap from Docker container

Summary of steps:

- Create `dockerfile`
- Create `build-zenmap.sh` to compile Zenmap (nmap)
- Run `build-zenmap.sh` to create `zenmap.tar.bz2`

### Save the following as `dockerfile`

```bash linenums="1"
cat << "EOF" > dockerfile
FROM debian:bookworm AS builder

ARG NMAP_VERSION=7.991
ARG DEBIAN_FRONTEND=noninteractive

ENV NMAP_VERSION=${NMAP_VERSION}

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        wget \
        bzip2 \
        xz-utils \
        file \
        pkg-config \
        autoconf \
        automake \
        libtool \
        python3 \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        libssl-dev \
        libpcap-dev \
        libpcre2-dev \
        libssh2-1-dev \
        liblinear-dev \
        zlib1g-dev \
        liblua5.4-dev \
        libgtk-3-dev \
        libgirepository1.0-dev \
        gir1.2-gtk-3.0 \
        python3-gi \
        python3-cairo \
        desktop-file-utils \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /build

RUN wget -O "nmap-${NMAP_VERSION}.tar.bz2" \
        "https://nmap.org/dist/nmap-${NMAP_VERSION}.tar.bz2" && \
    tar -xjf "nmap-${NMAP_VERSION}.tar.bz2"

WORKDIR /build/nmap-${NMAP_VERSION}

RUN ./configure \
        --prefix=/usr/local \
        --with-openssl \
        --with-libpcap \
        --with-libpcre \
        --with-libz \
        --with-liblua \
        --without-zenmap && \
    make -j"$(nproc)"

RUN mkdir -p /stage && \
    make DESTDIR=/stage install

WORKDIR /build

RUN wget -O "zenmap-${NMAP_VERSION}-py3-none-any.whl" \
        "https://nmap.org/dist/zenmap-${NMAP_VERSION}-py3-none-any.whl"

RUN mkdir -p /stage/packages && \
    cp "zenmap-${NMAP_VERSION}-py3-none-any.whl" /stage/packages/

RUN python3 -m pip install \
        --break-system-packages \
        --no-cache-dir \
        --no-deps \
        --root=/stage \
        --prefix=/usr/local \
        "zenmap-${NMAP_VERSION}-py3-none-any.whl"

RUN mkdir -p /stage/usr/local/share/doc/nmap && \
    cp "/build/nmap-${NMAP_VERSION}/LICENSE" \
       /stage/usr/local/share/doc/nmap/LICENSE

# Collect the complete ELF runtime dependency closure for the staged Nmap
# executables. Libraries are copied under /stage/data_dir while preserving
# their absolute filesystem paths. On Debian Bookworm with usrmerge, ldd may
# report libraries under either /lib/... or /usr/lib/..., so preserve the
# path returned by ldd rather than assuming one location.
RUN set -eux; \
    mkdir -p /stage/data_dir; \
    for bin in nmap ncat nping; do \
        exe="/stage/usr/local/bin/${bin}"; \
        [ -x "${exe}" ] || continue; \
        echo "===== Runtime libraries for ${bin} ====="; \
        ldd "${exe}"; \
        ldd "${exe}" | awk '/=> \// {print $3} /^\// {print $1}'; \
    done | awk '/^\// {print}' | sort -u > /tmp/runtime-libs.txt; \
    while IFS= read -r lib; do \
        [ -e "${lib}" ] || { echo "ERROR: unresolved runtime library: ${lib}" >&2; exit 1; }; \
        dest="/stage/data_dir${lib}"; \
        mkdir -p "$(dirname "${dest}")"; \
        cp -L "${lib}" "${dest}"; \
    done < /tmp/runtime-libs.txt; \
    echo "===== Collected runtime libraries ====="; \
    cat /tmp/runtime-libs.txt; \
    liblinear_path="$(find /stage/data_dir -type f -name 'liblinear.so.4' -print -quit)"; \
    [ -n "${liblinear_path}" ] || { echo "ERROR: liblinear.so.4 was not collected" >&2; exit 1; }; \
    echo "Verified liblinear.so.4: ${liblinear_path}"

# Zenmap/RadialNet requires the Debian Python Cairo bindings at runtime.
# The Zenmap wheel itself does not vendor pycairo, so copy the files from
# python3-cairo into data_dir while preserving their Debian filesystem paths.
RUN set -eux; \
    dpkg-query -L python3-cairo | while IFS= read -r path; do \
        [ -f "${path}" ] || [ -L "${path}" ] || continue; \
        dest="/stage/data_dir${path}"; \
        mkdir -p "$(dirname "${dest}")"; \
        cp -a "${path}" "${dest}"; \
    done; \
    cairo_module="$(find /stage/data_dir/usr/lib/python3/dist-packages -maxdepth 2 \
        \( -name 'cairo*.so' -o -name 'cairo' \) -print -quit)"; \
    [ -n "${cairo_module}" ] || { echo "ERROR: python3-cairo was not staged" >&2; exit 1; }; \
    echo "Verified Python Cairo runtime: ${cairo_module}"; \
    PYTHONPATH=/stage/data_dir/usr/lib/python3/dist-packages \
        python3 -c 'import cairo; print("cairo import OK:", cairo.__file__)'

RUN find /stage/usr/local/bin -type f -exec sh -c \
        'file "$1" | grep -q ELF && strip --strip-unneeded "$1" || true' \
        sh {} \;

RUN echo "===== Nmap build complete =====" && \
    /stage/usr/local/bin/nmap --version && \
    echo "===== staged files =====" && \
    find /stage/usr/local -maxdepth 4 -type f | sort

FROM debian:bookworm AS export
COPY --from=builder /stage /output
WORKDIR /output
CMD ["/bin/bash"]
EOF
```

### Save the following as `build-zenmap.sh`

```bash linenums="1"
cat << "EEOFF" > build-zenmap.sh
#!/bin/bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-nmap-zenmap-bookworm-builder}"
OUTPUT_DIR="${OUTPUT_DIR:-$(pwd)/output}"

echo "Detecting latest stable Nmap version from nmap.org ..."

NMAP_VERSION="$(
    curl -fsSL https://nmap.org/dist/ |
    grep -oE 'nmap-[0-9]+\.[0-9]+(\.[0-9]+)?\.tar\.bz2' |
    sed -E 's/^nmap-//; s/\.tar\.bz2$//' |
    sort -V |
    tail -1
)"

if [ -z "${NMAP_VERSION}" ]; then
    echo "ERROR: Unable to determine the latest Nmap version." >&2
    exit 1
fi

echo "Building Nmap/Zenmap ${NMAP_VERSION} on Debian Bookworm"

docker system prune -f

docker build --network host \
    --build-arg "NMAP_VERSION=${NMAP_VERSION}" \
    --target export \
    -t "${IMAGE_NAME}:${NMAP_VERSION}" \
    .

rm -rf "${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}"

CONTAINER_ID="$(docker create "${IMAGE_NAME}:${NMAP_VERSION}")"
trap 'docker rm -f "${CONTAINER_ID}" >/dev/null 2>&1 || true' EXIT

docker cp "${CONTAINER_ID}:/output/." "${OUTPUT_DIR}/"

docker rm "${CONTAINER_ID}" >/dev/null
trap - EXIT

cat > "${OUTPUT_DIR}/BUILD-INFO.txt" <<EOF
Nmap/Zenmap version: ${NMAP_VERSION}
Build base: Debian Bookworm
Source: https://nmap.org/dist/
Image: ${IMAGE_NAME}:${NMAP_VERSION}
EOF

echo
echo "Build complete."
echo "Output directory: ${OUTPUT_DIR}"
echo
echo "Nmap:   ${OUTPUT_DIR}/usr/local/bin/nmap"
echo "Ncat:   ${OUTPUT_DIR}/usr/local/bin/ncat"
echo "Nping:  ${OUTPUT_DIR}/usr/local/bin/nping"
echo "Zenmap: ${OUTPUT_DIR}/usr/local/bin/zenmap"
echo "Wheel:  ${OUTPUT_DIR}/packages/zenmap-${NMAP_VERSION}-py3-none-any.whl"
echo "Runtime libraries: ${OUTPUT_DIR}/data_dir/"
echo "LIBLINEAR: ${OUTPUT_DIR}/data_dir/usr/lib/x86_64-linux-gnu/liblinear.so.4"

# create tar.bz2 file
cp -a "${OUTPUT_DIR}"/usr/local/local/* "${OUTPUT_DIR}"/usr/local
rm -rf "${OUTPUT_DIR}"/usr/local/local
mkdir -p "${OUTPUT_DIR}"/lib/x86_64-linux-gnu/
cp -a "${OUTPUT_DIR}"/data_dir/lib/x86_64-linux-gnu/liblinear.so.4 "${OUTPUT_DIR}"/lib/x86_64-linux-gnu
pushd .
cd "${OUTPUT_DIR}"
tar -cvjf zenmap.tar.bz2 lib usr
popd
mv "${OUTPUT_DIR}/zenmap.tar.bz2" .

#
# Set the following for nmap file as IGEL OS Custom Command
# setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip /services/zenmap/usr/local/bin/nmap
#
EEOFF
chmod a+rx build-zenmap.sh
```
