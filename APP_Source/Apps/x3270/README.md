THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# [x3270](https://x3270.miraheze.org/wiki/Main_Page)

## Build x3270 from Docker container

Summary of steps:

- Create `dockerfile`
- Create `export.sh` to export latest x3270
- Create `build-x3270.sh` to compile latest x3270
- Run `build-x3270.sh` to create `x3270.tar.bz2`

### Save the following as `dockerfile`

```bash linenums="1"
cat << "EEOFF" > dockerfile
FROM debian:12-slim

ARG DEBIAN_FRONTEND=noninteractive
ARG X3270_VERSION=4.5ga6
ARG X3270_SERIES=04.05

ENV X3270_VERSION="${X3270_VERSION}" \
    X3270_SERIES="${X3270_SERIES}" \
    SRC_DIR=/usr/src/x3270 \
    STAGE_DIR=/opt/x3270-stage

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    file \
    pkg-config \
    dpkg-dev \
    python3 \
    tcl \
    tcl-dev \
    libexpat1-dev \
    libssl-dev \
    libx11-dev \
    libxt-dev \
    libxmu-dev \
    libxaw7-dev \
    libncursesw5-dev \
    libreadline-dev \
    xfonts-100dpi \
    xfonts-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src

RUN set -eux; \
    archive="suite3270-${X3270_VERSION}-src.tgz"; \
    url="https://x3270.bgp.nu/download/${X3270_SERIES}/${archive}"; \
    echo "Downloading ${url}"; \
    curl -fL --retry 3 --retry-delay 2 -o "/tmp/${archive}" "${url}"; \
    mkdir -p "${SRC_DIR}"; \
    tar -xzf "/tmp/${archive}" -C "${SRC_DIR}" --strip-components=1; \
    rm -f "/tmp/${archive}"

WORKDIR /usr/src/x3270

RUN set -eux; \
    ./configure --prefix=/usr/local; \
    make -j"$(nproc)"; \
    rm -rf "${STAGE_DIR}"; \
    make DESTDIR="${STAGE_DIR}" install

COPY export.sh /usr/local/bin/export-x3270
RUN chmod 0755 /usr/local/bin/export-x3270

ENTRYPOINT ["/usr/local/bin/export-x3270"]
EEOFF
```

### Save the following as `export.sh`

```bash linenums="1"
cat << "EEOFF" > export.sh
#!/bin/sh
set -eu

OUT=/output
DATA_DIR="${OUT}/data_dir"
INFO_DIR="${OUT}/build-info"
STAGE="${STAGE_DIR:-/opt/x3270-stage}"

echo "x3270 Bookworm runtime packager"
echo "x3270 version: ${X3270_VERSION:-unknown}"

rm -rf "${OUT:?}/"*
mkdir -p "${DATA_DIR}" "${INFO_DIR}"

copy_preserve_path() {
    src="$1"
    [ -e "$src" ] || return 0

    case "$src" in
        /*) rel="${src#/}" ;;
        *)  echo "Skipping non-absolute path: $src" >&2; return 0 ;;
    esac

    dst="${DATA_DIR}/${rel}"
    mkdir -p "$(dirname "$dst")"

    if [ -L "$src" ]; then
        # Preserve the symlink itself.
        cp -a "$src" "$dst"

        # Also copy its real target, preserving the target's absolute path.
        target="$(readlink -f "$src" 2>/dev/null || true)"
        if [ -n "$target" ] && [ -e "$target" ]; then
            copy_preserve_path "$target"
        fi
    elif [ -f "$src" ]; then
        cp -a "$src" "$dst"
    fi
}

# Copy the suite's installed /usr/local tree first. This includes executables,
# resources, scripts, man pages and any x3270-specific support files.
if [ -d "${STAGE}/usr/local" ]; then
    mkdir -p "${DATA_DIR}/usr"
    cp -a "${STAGE}/usr/local" "${DATA_DIR}/usr/"
fi

# Runtime dependency closure.
# Seed with every ELF executable or shared object installed by the suite.
QUEUE="$(mktemp)"
NEXT="$(mktemp)"
SEEN="$(mktemp)"
LIBS="$(mktemp)"
PKGS="$(mktemp)"
trap 'rm -f "$QUEUE" "$NEXT" "$SEEN" "$LIBS" "$PKGS"' EXIT

find "${STAGE}/usr/local" -type f -print0 |
while IFS= read -r -d '' f; do
    if file -b "$f" | grep -q 'ELF '; then
        printf '%s\n' "$f"
    fi
done | sort -u > "$QUEUE"

: > "$SEEN"
: > "$LIBS"
: > "$PKGS"

while [ -s "$QUEUE" ]; do
    : > "$NEXT"

    while IFS= read -r obj; do
        [ -n "$obj" ] || continue

        if grep -Fqx "$obj" "$SEEN"; then
            continue
        fi
        printf '%s\n' "$obj" >> "$SEEN"

        # ldd output forms handled:
        #   libX.so => /path/libX.so (...)
        #   /lib64/ld-linux-x86-64.so.2 (...)
        ldd "$obj" 2>/dev/null |
        awk '
            $2 == "=>" && $3 ~ /^\// { print $3 }
            $1 ~ /^\// { print $1 }
        ' |
        while IFS= read -r lib; do
            [ -n "$lib" ] || continue
            printf '%s\n' "$lib" >> "$LIBS"
            printf '%s\n' "$lib" >> "$NEXT"
        done
    done < "$QUEUE"

    sort -u "$NEXT" -o "$NEXT"
    mv "$NEXT" "$QUEUE"
    NEXT="$(mktemp)"
done

sort -u "$LIBS" -o "$LIBS"

# Copy only the runtime libraries ldd says are required.
while IFS= read -r lib; do
    [ -n "$lib" ] || continue
    copy_preserve_path "$lib"

    # Record owning Debian package, if any.
    pkg="$(dpkg-query -S "$lib" 2>/dev/null | head -n1 | cut -d: -f1 || true)"
    if [ -n "$pkg" ]; then
        printf '%s\n' "$pkg" >> "$PKGS"
    fi
done < "$LIBS"

sort -u "$PKGS" -o "$PKGS"

# Copy X11 font files that x3270 commonly requires at runtime.
for d in \
    /usr/share/fonts/X11/100dpi \
    /usr/share/fonts/X11/misc
do
    if [ -d "$d" ]; then
        find "$d" -maxdepth 1 -type f \( -iname '*3270*' -o -iname 'fonts.dir' -o -iname 'fonts.alias' -o -iname 'fonts.scale' \) |
        while IFS= read -r f; do
            copy_preserve_path "$f"
        done
    fi
done

# Capture version and dependency diagnostics.
{
    echo "X3270_VERSION=${X3270_VERSION:-unknown}"
    echo "X3270_SERIES=${X3270_SERIES:-unknown}"
    echo "BUILD_DATE_UTC=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    echo
    echo "Suite-installed ELF objects:"
    cat "$SEEN"
} > "${INFO_DIR}/build.txt"

cp "$LIBS" "${INFO_DIR}/runtime-libraries.txt"
cp "$PKGS" "${INFO_DIR}/runtime-packages.txt"

: > "${INFO_DIR}/ldd.txt"
for f in \
    "${STAGE}/usr/local/bin/x3270" \
    "${STAGE}/usr/local/bin/c3270" \
    "${STAGE}/usr/local/bin/s3270" \
    "${STAGE}/usr/local/bin/pr3287" \
    "${STAGE}/usr/local/bin/b3270" \
    "${STAGE}/usr/local/bin/tcl3270"
do
    if [ -x "$f" ] && file -b "$f" | grep -q 'ELF '; then
        {
            echo "===== ${f#${STAGE}} ====="
            ldd "$f" || true
            echo
        } >> "${INFO_DIR}/ldd.txt"
    fi
done

# Check the copied ELF files for unresolved dependencies using the current
# container as the reference environment.
: > "${INFO_DIR}/dependency-check.txt"
find "${DATA_DIR}" -type f -print0 |
while IFS= read -r -d '' f; do
    if file -b "$f" | grep -q 'ELF '; then
        missing="$(ldd "$f" 2>/dev/null | grep 'not found' || true)"
        if [ -n "$missing" ]; then
            {
                echo "===== $f ====="
                echo "$missing"
                echo
            } >> "${INFO_DIR}/dependency-check.txt"
        fi
    fi
done

if [ -s "${INFO_DIR}/dependency-check.txt" ]; then
    echo "WARNING: unresolved libraries were detected:"
    cat "${INFO_DIR}/dependency-check.txt"
else
    echo "Dependency check: no unresolved libraries detected."
    echo "No unresolved libraries detected." > "${INFO_DIR}/dependency-check.txt"
fi

echo
echo "Debian Bookworm runtime packages:"
cat "${INFO_DIR}/runtime-packages.txt" || true

echo
echo "Runtime bundle created under:"
echo "  ${DATA_DIR}"

du -sh "${DATA_DIR}" || true
EEOFF
```

### Save the following as `build-x3270.sh`

```bash linenums="1"
cat << "EEOFF" > build-x3270.sh
#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

IMAGE_NAME="${IMAGE_NAME:-x3270-bookworm-builder}"
X3270_VERSION="${X3270_VERSION:-4.5ga6}"
X3270_SERIES="${X3270_SERIES:-04.05}"
OUTPUT_DIR="${OUTPUT_DIR:-$(pwd)/output}"

mkdir -p "$OUTPUT_DIR"

echo "============================================================"
echo " Building x3270"
echo "============================================================"
echo "Image:          ${IMAGE_NAME}:${X3270_VERSION}"
echo "x3270 version:  ${X3270_VERSION}"
echo "x3270 series:   ${X3270_SERIES}"
echo "Output:         ${OUTPUT_DIR}"
echo

docker system prune -f

docker build --network host \
    --pull \
    --build-arg "X3270_VERSION=${X3270_VERSION}" \
    --build-arg "X3270_SERIES=${X3270_SERIES}" \
    -t "${IMAGE_NAME}:${X3270_VERSION}" \
    .

echo
echo "============================================================"
echo " Exporting runtime data_dir"
echo "============================================================"

docker run --rm --network host \
    -v "${OUTPUT_DIR}:/output" \
    "${IMAGE_NAME}:${X3270_VERSION}"

echo
echo "============================================================"
echo " Build completed"
echo "============================================================"

if [ -f "${OUTPUT_DIR}/build-info/runtime-packages.txt" ]; then
    echo
    echo "Debian Bookworm runtime packages:"
    cat "${OUTPUT_DIR}/build-info/runtime-packages.txt"
fi

if [ -f "${OUTPUT_DIR}/build-info/dependency-check.txt" ]; then
    echo
    echo "Dependency check:"
    cat "${OUTPUT_DIR}/build-info/dependency-check.txt"
fi

echo
echo "Output files:"
find "$OUTPUT_DIR" -maxdepth 4 -type f | sort

echo
echo "============================================================"
echo " Create x3270.tar.bz2"
echo "============================================================"

top_level_dir=$(pwd)
pushd .
cd "$OUTPUT_DIR"/data_dir
tar -cvjf ${top_level_dir}/x3270.tar.bz2 *
popd
EEOFF
chmod a+rx build-x3270.sh
```
