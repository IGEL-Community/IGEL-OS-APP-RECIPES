THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [Remmina](https://remmina.org/)

Remote access screen and file sharing to your desktop.

## Steps to create remmina.tar.bz2

### Obtain Remmina tar.bz2 file by running the following script on Ubuntu 20.04

```bash linenums="1"
#!/bin/bash
#set -x
#trap read debug

# Build package
APP="remmina"
ZIP_FILE="Remmina"
CLEAN="TRUE"
OS12_CLEAN="12.6.0"
GETVERSION_FILE="../../remmina_*.deb"
MISSING_LIBS="i965-va-driver intel-media-va-driver libaom0 libavahi-ui-gtk3-0 libavcodec58 libavutil56 libayatana-appindicator3-1 libayatana-indicator3-7 libcodec2-0.9 libfreerdp-client2-2 libfreerdp2-2 libgsm1 libigdgmm11 libshine3 libsnappy1v5 libswresample3 libva-drm2 libva-x11-2 libva2 libvdpau1 libvncclient1 libwebp6 libwinpr2-2 libx264-155 libx265-179 libxvidcore4 libzvbi-common libzvbi0 mesa-va-drivers mesa-vdpau-drivers ocl-icd-libopencl1 remmina remmina-common remmina-plugin-rdp remmina-plugin-secret remmina-plugin-vnc va-driver-all vdpau-driver-all libssh-4 libicu66 libvpx6"

# Remmina - add - repository
sudo apt-add-repository ppa:remmina-ppa-team/remmina-next -y
# Remmina - add - repository

sudo apt update -y

sudo apt install unzip -y

mkdir build_tar
cd build_tar

for lib in $MISSING_LIBS; do
  apt-get download $lib
done

mkdir -p custom/${APP}

find . -name "*.deb" | while read LINE
do
  dpkg -x "${LINE}" custom/${APP}
done

if [ "${CLEAN}" = "TRUE" ]; then
  echo "+++++++=======  STARTING CLEAN of USR =======+++++++"
  wget https://raw.githubusercontent.com/IGEL-Community/IGEL-Custom-Partitions/master/utils/igelos_usr/clean_cp_usr_lib.sh
  chmod a+x clean_cp_usr_lib.sh
  wget https://raw.githubusercontent.com/IGEL-Community/IGEL-Custom-Partitions/master/utils/igelos_usr/clean_cp_usr_share.sh
  chmod a+x clean_cp_usr_share.sh
  ./clean_cp_usr_lib.sh ${OS12_CLEAN}_usr_lib.txt custom/${APP}/usr/lib
  ./clean_cp_usr_share.sh ${OS12_CLEAN}_usr_share.txt custom/${APP}/usr/share
  echo "+++++++=======  DONE CLEAN of USR =======+++++++"
fi

cd custom/${APP}

# build tar.bz2
tar cvjf ../../../${APP}.tar.bz2 .

cd ../../..
rm -rf build_tar
```

### Obtain Remmina tar.bz2 file by running the following docker container

Summary of steps:

- Create `dockerfile`
- Create `build-remmina.sh` to create `remmina.tar.bz2`
- Create and run `run-docker`

### Save the following as `dockerfile`

```bash linenums="1"
cat << "EOF" > dockerfile
# syntax=docker/dockerfile:1

FROM debian:bookworm AS build

# Make RUN commands fail on pipeline errors and print useful diagnostics.
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /tmp

# Copy build context.
COPY . .
COPY build-remmina.sh .
COPY remmina-*.tar.gz .

# Base diagnostics + dependencies.
RUN set -eux; \
    echo "=== BUILD ENVIRONMENT ==="; \
    date --iso-8601=seconds; \
    cat /etc/os-release; \
    uname -a; \
    dpkg --print-architecture; \
    echo "=== APT SOURCES ==="; \
    grep -RhsE '^[[:space:]]*(deb|Types:|URIs:|Suites:|Components:)' /etc/apt/sources.list /etc/apt/sources.list.d || true; \
    echo "=== DIRECTORY CONTENTS ==="; \
    find /tmp -maxdepth 2 -type f -printf '%p %s bytes\n' | sort; \
    echo "=== APT UPDATE ==="; \
    apt-get update; \
    echo "=== INSTALL BUILD DEPENDENCIES ==="; \
    apt-get install -y --no-install-recommends curl gnupg ca-certificates bzip2; \
    echo "=== INSTALLED TOOL VERSIONS ==="; \
    bash --version; \
    apt-get --version; \
    dpkg --version

# Run collection/build script with shell tracing enabled.
RUN set -eux; \
    chmod +x ./build-remmina.sh; \
    echo "=== START build-remmina.sh ==="; \
    ./build-remmina.sh; \
    rc=$?; \
    echo "=== END build-remmina.sh rc=${rc} ==="; \
    exit "$rc"

# Copy final artifact and print metadata so it is visible in BuildKit logs.
RUN set -eux; \
    mkdir -p /out; \
    echo "=== GENERATED ARCHIVES ==="; \
    find /tmp -maxdepth 1 -type f -name '*.tar.bz2' -exec ls -lh {} \;; \
    cp -v /tmp/*.tar.bz2 /out/; \
    echo "=== EXPORT CONTENTS ==="; \
    find /out -maxdepth 1 -type f -exec ls -lh {} \;

FROM scratch AS export
COPY --from=build /out/ /
EOF
```

### Save the following as `build-remmina.sh`

```bash linenums="1"
cat << "EOF" > build-remmina.sh
#!/bin/bash

set -Eeuo pipefail

# Detailed shell tracing. PS4 adds timestamp, source file, line and function.
export PS4='+ $(date "+%Y-%m-%d %H:%M:%S") ${BASH_SOURCE##*/}:${LINENO}:${FUNCNAME[0]:-main}(): '
set -x

log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

on_error() {
    local rc=$?
    local line=${BASH_LINENO[0]:-unknown}
    local cmd=${BASH_COMMAND:-unknown}
    set +x
    printf '\n============================================================\n' >&2
    printf 'ERROR: build-remmina.sh failed\n' >&2
    printf 'Return code : %s\n' "$rc" >&2
    printf 'Line        : %s\n' "$line" >&2
    printf 'Command     : %s\n' "$cmd" >&2
    printf 'PWD         : %s\n' "$PWD" >&2
    printf 'Date        : %s\n' "$(date --iso-8601=seconds)" >&2
    printf '============================================================\n\n' >&2
    exit "$rc"
}
trap on_error ERR

# Build package
APP="remmina"
ZIP_FILE="Remmina"
CLEAN="TRUE"
OS12_CLEAN="12.6.0"
GETVERSION_FILE="../../remmina_*.deb"
# Debian 12 Bookworm ABI package names.
# Updated from older Debian/Ubuntu-era names:
#   libaom0 -> libaom3
#   libavcodec58 -> libavcodec59
#   libavutil56 -> libavutil57
#   libcodec2-0.9 -> libcodec2-1.0
#   libigdgmm11 -> libigdgmm12
#   libswresample3 -> libswresample4
#   libwebp6 -> libwebp7
#   libx264-155 -> libx264-164
#   libx265-179 -> libx265-199
#   libicu66 -> libicu72
#   libvpx6 -> libvpx7
MISSING_LIBS="i965-va-driver intel-media-va-driver libaom3 libavahi-ui-gtk3-0 libavcodec59 libavutil57 libayatana-appindicator3-1 libayatana-indicator3-7 libcodec2-1.0 libfreerdp-client2-2 libfreerdp2-2 libgsm1 libigdgmm12 libshine3 libsnappy1v5 libswresample4 libva-drm2 libva-x11-2 libva2 libvdpau1 libvncclient1 libwebp7 libwinpr2-2 libx264-164 libx265-199 libxvidcore4 libzvbi-common libzvbi0 mesa-va-drivers mesa-vdpau-drivers ocl-icd-libopencl1 remmina remmina-common remmina-plugin-rdp remmina-plugin-secret remmina-plugin-vnc va-driver-all vdpau-driver-all libssh-4 libicu72 libvpx7"

log "Starting Remmina package collection"
log "APP=${APP}"
log "Debian release: $(cat /etc/debian_version 2>/dev/null || echo unknown)"
log "Architecture: $(dpkg --print-architecture 2>/dev/null || uname -m)"
log "Kernel: $(uname -a)"
log "Working directory: ${PWD}"
log "APT sources:"
grep -RhsE '^[[:space:]]*(deb|Types:|URIs:|Suites:|Components:)' /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null || true
log "APT configuration:"
apt-config dump 2>/dev/null || true

rm -rf build_tar
mkdir -p build_tar
cd build_tar

log "Checking/downloading requested packages"
failed_packages=()
downloaded_packages=0

for lib in $MISSING_LIBS; do
    log "------------------------------------------------------------"
    log "Package: ${lib}"

    # Show whether APT knows about the package and what versions are candidates.
    apt-cache policy "$lib" 2>/dev/null || true

    if apt-get download "$lib"; then
        downloaded_packages=$((downloaded_packages + 1))
        log "SUCCESS: downloaded ${lib}"
    else
        rc=$?
        log "ERROR: apt-get download failed for ${lib} (rc=${rc})"
        failed_packages+=("${lib}")
    fi
done

log "Download phase complete"
log "Successful package downloads: ${downloaded_packages}"
log "Downloaded .deb files:"
find . -maxdepth 1 -type f -name '*.deb' -printf '%f\n' | sort || true

if ((${#failed_packages[@]} > 0)); then
    set +x
    printf '\nERROR: %d package(s) failed to download:\n' "${#failed_packages[@]}" >&2
    printf '  - %s\n' "${failed_packages[@]}" >&2
    printf '\nAPT search results for failed package names:\n' >&2
    for lib in "${failed_packages[@]}"; do
        printf '\n### %s ###\n' "$lib" >&2
        apt-cache search --names-only "^${lib}$" 2>/dev/null >&2 || true
    done
    exit 20
fi

mkdir -p "custom/${APP}"

log "Extracting downloaded Debian packages"
extracted=0
while IFS= read -r -d '' deb; do
    log "Extracting: ${deb}"
    dpkg-deb --info "$deb" | sed -n '1,20p' || true
    dpkg -x "$deb" "custom/${APP}"
    extracted=$((extracted + 1))
done < <(find . -type f -name '*.deb' -print0)
log "Extracted ${extracted} package(s)"

if ((extracted == 0)); then
    log "ERROR: no .deb files were found to extract"
    exit 21
fi

log "Resulting custom partition size before archive:"
du -sh "custom/${APP}" || true
log "Top-level output directories:"
find "custom/${APP}" -maxdepth 3 -type d | sort | head -200 || true

cd "custom/${APP}"

log "Checking archive compression tools"
command -v tar
command -v bzip2
tar --version
bzip2 --version 2>&1 || true

log "Creating ../../../${APP}.tar.bz2"
tar -cvjf "../../../${APP}.tar.bz2" .

cd ../../..

log "Archive created:"
ls -lh "${APP}.tar.bz2"
log "Archive test/listing (first 100 entries):"
tar -tjf "${APP}.tar.bz2" | head -100 || true

rm -rf build_tar
log "Build completed successfully"
EOF
```

### Save the following as `run-docker.sh` and run it:

```bash linenums="1"
cat << "EOF" > run-docker.sh
#!/bin/bash

set -Eeuo pipefail

export PS4='+ $(date "+%Y-%m-%d %H:%M:%S") ${BASH_SOURCE##*/}:${LINENO}: '
set -x

LOG_DIR="${LOG_DIR:-./logs}"
ARTIFACT_DIR="${ARTIFACT_DIR:-./artifacts}"
BUILD_LOG="${LOG_DIR}/docker-build-$(date '+%Y%m%d-%H%M%S').log"

mkdir -p "$LOG_DIR" "$ARTIFACT_DIR"

on_error() {
    local rc=$?
    set +x
    printf '\nDocker build failed with return code %s\n' "$rc" >&2
    printf 'Full build log: %s\n' "$BUILD_LOG" >&2
    printf 'Last 100 log lines:\n' >&2
    tail -100 "$BUILD_LOG" >&2 || true
    exit "$rc"
}
trap on_error ERR

{
    echo "============================================================"
    echo "Docker build debug run"
    echo "Date: $(date --iso-8601=seconds)"
    echo "PWD:  $PWD"
    echo "Host: $(uname -a)"
    echo "============================================================"
    echo
    echo "=== Docker version ==="
    docker version
    echo
    echo "=== Docker info ==="
    docker info
    echo
    echo "=== Buildx version ==="
    docker buildx version
    echo
    echo "=== Buildx builders ==="
    docker buildx ls
    echo
    echo "=== Disk usage before prune ==="
    docker system df
    echo
    echo "=== Docker system prune ==="
    docker system prune -f
    echo
    echo "=== Disk usage after prune ==="
    docker system df
    echo
    echo "=== Build context ==="
    find . -maxdepth 2 -type f -printf '%p %s bytes\n' | sort
    echo
    echo "=== Starting build ==="
} 2>&1 | tee "$BUILD_LOG"

# BUILDKIT_PROGRESS=plain disables the condensed TTY UI and preserves every line.
# --progress=plain makes RUN output directly visible.
# --no-cache can be enabled with NO_CACHE=1 for maximum reproducibility/debugging.
build_args=(
    --network host
    --progress=plain
    --target export
    --output "type=local,dest=${ARTIFACT_DIR}"
)

if [[ "${NO_CACHE:-0}" == "1" ]]; then
    build_args+=(--no-cache)
fi

BUILDKIT_PROGRESS=plain docker buildx build "${build_args[@]}" . 2>&1 | tee -a "$BUILD_LOG"

{
    echo
    echo "=== Build completed successfully ==="
    echo "Artifacts:"
    find "$ARTIFACT_DIR" -maxdepth 2 -type f -exec ls -lh {} \;
    echo "SHA256:"
    find "$ARTIFACT_DIR" -maxdepth 2 -type f -exec sha256sum {} \;
    echo "Full log: $BUILD_LOG"
} 2>&1 | tee -a "$BUILD_LOG"
EOF
```