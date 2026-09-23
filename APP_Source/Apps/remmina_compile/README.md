THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [Remmina](https://remmina.org/)

Remote access screen and file sharing to your desktop.

- Determine latest Remmina version [GitLab](https://gitlab.com/Remmina/Remmina/-/releases)
- Determine latest FreeRDP version [GitHub](https://github.com/FreeRDP/FreeRDP/releases)

## Use Docker to compile the latest version of Remmina and FreeRDP

Summary of steps:

- Create `dockerfile`
- Create `build-remmina_compile.sh` to create `remmina_compile.tar.bz2`

**NOTE:** Update the scripts for the version number to build

### Save the following as `dockerfile`

```bash linenums="1"
cat << "EOF" > dockerfile
# syntax=docker/dockerfile:1.7
ARG DEBIAN_VERSION=bookworm
FROM debian:${DEBIAN_VERSION} AS builder

ARG DEBIAN_FRONTEND=noninteractive
ARG FREERDP_REF=3.32.0
ARG REMMINA_REF=v1.4.43
ARG BUILD_TYPE=Release
ARG JOBS=0

ENV PREFIX=/usr/local \
    STAGE=/output/data_dir \
    PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:/usr/local/lib/x86_64-linux-gnu/pkgconfig:/usr/local/share/pkgconfig \
    CMAKE_PREFIX_PATH=/usr/local \
    LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib/x86_64-linux-gnu

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      build-essential ca-certificates git cmake ninja-build pkg-config \
      gettext intltool xsltproc xmlto docbook-xsl \
      libssl-dev libkrb5-dev libz-dev libjpeg62-turbo-dev \
      libx11-dev libxext-dev libxinerama-dev libxcursor-dev libxdamage-dev \
      libxv-dev libxkbfile-dev libxkbcommon-dev libxrandr-dev libxi-dev \
      libxrender-dev libxfixes-dev libxtst-dev libx264-dev \
      libwayland-dev wayland-protocols \
      libasound2-dev libpulse-dev libcups2-dev libpcsclite-dev \
      libusb-1.0-0-dev libudev-dev uuid-dev libxml2-dev \
      libavcodec-dev libavutil-dev libswresample-dev \
      libopus-dev libgsm1-dev libsoxr-dev libcjson-dev \
      libpam0g-dev libpkcs11-helper1-dev \
      libgtk-3-dev libglib2.0-dev libpango1.0-dev libcairo2-dev \
      libgdk-pixbuf-2.0-dev libsecret-1-dev libssh-dev libssh-4 \
      libcurl4-openssl-dev libsodium-dev libgcrypt20-dev \
      libavahi-client-dev libavahi-ui-gtk3-dev libavahi-ui-gtk3-0 \
      desktop-file-utils shared-mime-info \
      file patchelf \
      libvte-2.91-dev \
      libayatana-appindicator3-dev \
      libjson-glib-dev \
      libfuse3-dev \
      libavcodec-dev \
      libavutil-dev \
      libswscale-dev; \ 
    rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Build and install FreeRDP first. Remmina is then linked against this exact build.
RUN set -eux; \
    git clone --filter=blob:none --recurse-submodules https://github.com/FreeRDP/FreeRDP.git freerdp; \
    cd freerdp; \
    git checkout "${FREERDP_REF}"; \
    git submodule update --init --recursive; \
    if [ "${JOBS}" = "0" ]; then JOBS="$(nproc)"; fi; \
    cmake -S . -B build -G Ninja \
      -DCMAKE_BUILD_TYPE="${BUILD_TYPE}" \
      -DCMAKE_INSTALL_PREFIX="${PREFIX}" \
      -DBUILD_SHARED_LIBS=ON \
      -DBUILD_TESTING=OFF \
      -DWITH_SERVER=OFF \
      -DWITH_SHADOW=OFF \
      -DWITH_PROXY=OFF \
      -DWITH_SDL=OFF \
      -DWITH_X11=ON \
      -DWITH_WAYLAND=ON \
      -DWITH_PULSE=ON \
      -DWITH_ALSA=ON \
      -DWITH_CUPS=ON \
      -DWITH_PCSC=ON; \
    cmake --build build --parallel "${JOBS}"; \
    cmake --install build; \
    DESTDIR="${STAGE}" cmake --install build; \
    ldconfig

# Build Remmina from source using the FreeRDP 3 libraries above.
RUN set -eux; \
    git clone --filter=blob:none --recurse-submodules https://gitlab.com/Remmina/Remmina.git remmina; \
    cd remmina; \
    git checkout "${REMMINA_REF}"; \
    git submodule update --init --recursive; \
    if [ "${JOBS}" = "0" ]; then JOBS="$(nproc)"; fi; \
    cmake -S . -B build -G Ninja \
      -DCMAKE_BUILD_TYPE="${BUILD_TYPE}" \
      -DCMAKE_INSTALL_PREFIX="${PREFIX}" \
      -DCMAKE_PREFIX_PATH="${PREFIX}" \
      -DWITH_FREERDP3=ON \
      -DWITH_APPINDICATOR=OFF \
      -DWITH_KF5WALLET=OFF \
      -DWITH_GVNC=OFF \
      -DWITH_LIBVNCSERVER=OFF \
      -DWITH_X2GO=OFF \
      -DWITH_WWW=OFF \
      -DWITH_PYTHONLIBS=OFF \
      -DWITH_NEWS=OFF \
      -DWITH_STATS=OFF \
      -DWITH_TIP=OFF \
      -DWITH_MANPAGES=OFF \
      -DWITH_TRANSLATIONS=ON; \
    cmake --build build --parallel "${JOBS}"; \
    cmake --install build; \
    DESTDIR="${STAGE}" cmake --install build; \
    ldconfig

# Record versions/build configuration and collect Debian runtime libraries needed
# by staged ELF executables and shared libraries. /usr/local dependencies are
# already staged by the two source installs above.
RUN set -eux; \
    mkdir -p /output/build-info; \
    printf 'FreeRDP ref: %s\nRemmina ref: %s\nBuild type: %s\n' \
      "${FREERDP_REF}" "${REMMINA_REF}" "${BUILD_TYPE}" \
      > /output/build-info/versions.txt; \
    /usr/local/bin/xfreerdp --version >> /output/build-info/versions.txt 2>&1 || true; \
    /usr/local/bin/remmina --version >> /output/build-info/versions.txt 2>&1 || true; \
    mkdir -p "${STAGE}${PREFIX}/lib"; \
    for soname in libssh.so.4 libavahi-ui-gtk3.so.0; do \
      lib="$(ldconfig -p | awk -v n="$soname" '$1 == n { print $NF; exit }')"; \
      if [ -z "$lib" ] || [ ! -e "$lib" ]; then \
        echo "ERROR: runtime library $soname is installed but could not be located" >&2; \
        exit 1; \
      fi; \
      real="$(readlink -f "$lib")"; \
      cp -a "$real" "${STAGE}${PREFIX}/lib/"; \
      ln -sf "$(basename "$real")" "${STAGE}${PREFIX}/lib/$soname"; \
    done; \
    : > /output/build-info/runtime-libraries.txt; \
    : > /output/build-info/runtime-packages.txt; \
    : > /output/build-info/unresolved-libraries.txt; \
    find "${STAGE}" -type f \( -perm -0100 -o -name '*.so' -o -name '*.so.*' \) -print0 \
      | while IFS= read -r -d '' f; do \
          if file -b "$f" | grep -q ELF; then \
            ldd "$f" 2>/dev/null || true; \
          fi; \
        done \
      | tee /tmp/ldd-all.txt >/dev/null; \
    awk '/=> not found/{print $1}' /tmp/ldd-all.txt | sort -u \
      > /output/build-info/unresolved-libraries.txt; \
    { \
      awk '/=> \/(lib|usr\/lib)\//{print $3}' /tmp/ldd-all.txt; \
      awk '/^[[:space:]]*\/(lib|usr\/lib)\//{print $1}' /tmp/ldd-all.txt; \
    } | sed '/^$/d' | sort -u > /tmp/runtime-libs.txt; \
    while IFS= read -r lib; do \
      [ -e "$lib" ] || continue; \
      case "$lib" in /usr/local/*) continue ;; esac; \
      echo "$lib" >> /output/build-info/runtime-libraries.txt; \
      cp -a --parents "$lib" "${STAGE}"; \
      real="$(readlink -f "$lib" || true)"; \
      if [ -n "$real" ] && [ "$real" != "$lib" ] && [ -e "$real" ]; then \
        cp -a --parents "$real" "${STAGE}"; \
      fi; \
      dpkg-query -S "$lib" 2>/dev/null | cut -d: -f1 >> /output/build-info/runtime-packages.txt || true; \
    done < /tmp/runtime-libs.txt; \
    sort -u -o /output/build-info/runtime-libraries.txt /output/build-info/runtime-libraries.txt; \
    sort -u -o /output/build-info/runtime-packages.txt /output/build-info/runtime-packages.txt; \
    rm -rf \
      "${STAGE}/usr/local/include" \
      "${STAGE}/usr/local/lib/cmake" \
      "${STAGE}/usr/local/share/applications"; \
    find "${STAGE}" -type l -printf '%p -> %l\n' | sort > /output/build-info/symlinks.txt; \
    find "${STAGE}" \( -type f -o -type l \) | sort > /output/build-info/files.txt

FROM scratch AS export
COPY --from=builder /output/ /
EOF
```

### Save the following as `build-remmina_compile.sh`

```bash linenums="1"
cat << "EOF" > build-remmina_compile.sh
#!/usr/bin/env bash
set -euo pipefail

FREERDP_REF="${FREERDP_REF:-3.32.0}"
REMMINA_REF="${REMMINA_REF:-v1.4.43}"
BUILD_TYPE="${BUILD_TYPE:-Release}"
OUTPUT_DIR="${OUTPUT_DIR:-output}"

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

docker system prune -f

docker build \
  --network host \
  --target export \
  --build-arg "FREERDP_REF=$FREERDP_REF" \
  --build-arg "REMMINA_REF=$REMMINA_REF" \
  --build-arg "BUILD_TYPE=$BUILD_TYPE" \
  --output "type=local,dest=$OUTPUT_DIR" \
  .

printf '\nBuild complete.\n'
printf '  FreeRDP: %s\n' "$FREERDP_REF"
printf '  Remmina: %s\n' "$REMMINA_REF"
printf '  Output:  %s/data_dir\n\n' "$OUTPUT_DIR"

if [ -f "$OUTPUT_DIR/build-info/versions.txt" ]; then
  cat "$OUTPUT_DIR/build-info/versions.txt"
fi

#
# create tar.bz2
#
pushd .
cd output/data_dir
tar cvjf ../../remmina_compile.tar.bz2 .
popd
EOF
chmod a+x build-remmina_compile.sh
```
