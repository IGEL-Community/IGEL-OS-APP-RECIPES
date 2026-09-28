#!/bin/bash
#set -x
#trap read debug

#
# This script compares the files in a targets directories before and after some changes,
# identifying new and modified files.
#
# Run as root
#

set -u

TARGETS=(
    "/bin"
    "/etc"
    "/lib"
    "/opt"
    "/sbin"
    "/userhome"
    "/usr"
    "/var"
)

WORKDIR="$(mktemp -d)"
BEFORE="$WORKDIR/before.sha256"
AFTER="$WORKDIR/after.sha256"

NEW_FILES="$WORKDIR/new_files.txt"
CHANGED_FILES="$WORKDIR/changed_files.txt"

#cleanup() {
    #rm -rf "$WORKDIR"
#}
#trap cleanup EXIT

#
# Verify target directories exist
#

for TARGET in "${TARGETS[@]}"; do
    if [ ! -d "$TARGET" ]; then
        echo "ERROR: Directory does not exist: $TARGET"
        exit 1
    fi
done

#
# Function to create a snapshot
#

create_snapshot() {
    local OUTPUT="$1"

    : > "$OUTPUT"

    for TARGET in "${TARGETS[@]}"; do
        find "$TARGET" -type f -print0 |
            sort -z |
            while IFS= read -r -d '' FILE; do
                HASH="$(sha256sum "$FILE" | awk '{print $1}')"
                printf '%s\t%s\n' "$FILE" "$HASH"
            done >> "$OUTPUT"
    done

    sort -o "$OUTPUT" "$OUTPUT"
}

echo
echo "Creating BEFORE snapshot..."
echo

for TARGET in "${TARGETS[@]}"; do
    echo "  $TARGET"
done

create_snapshot "$BEFORE"

echo
echo "============================================================"
echo " BEFORE SNAPSHOT COMPLETE"
echo "============================================================"
echo
echo "Now perform the required tasks/update."
echo
echo "When finished, return to this terminal."
echo

while true; do
    read -r -p "Have you completed the tasks? [y/N]: " ANSWER

    case "$ANSWER" in
        [Yy]|[Yy][Ee][Ss])
            break
            ;;
        [Nn]|[Nn][Oo]|"")
            echo
            echo "Complete the tasks, then answer yes when finished."
            echo
            ;;
        *)
            echo "Please answer yes or no."
            ;;
    esac
done

echo
echo "Creating AFTER snapshot..."

create_snapshot "$AFTER"

#
# Find NEW files
#

awk -F '\t' '
    NR==FNR {
        before[$1]=$2
        next
    }

    !($1 in before) {
        print $1
    }
' "$BEFORE" "$AFTER" > "$NEW_FILES"

#
# Find CHANGED files
#

awk -F '\t' '
    NR==FNR {
        before[$1]=$2
        next
    }

    ($1 in before) && before[$1] != $2 {
        print $1
    }
' "$BEFORE" "$AFTER" > "$CHANGED_FILES"

echo
echo "============================================================"
echo " NEW FILES"
echo "============================================================"

if [ -s "$NEW_FILES" ]; then
    cat "$NEW_FILES"
else
    echo "None"
fi

echo
echo "============================================================"
echo " CHANGED FILES"
echo "============================================================"

if [ -s "$CHANGED_FILES" ]; then
    cat "$CHANGED_FILES"
else
    echo "None"
fi

echo
echo "============================================================"
echo " Comparison complete"
echo "============================================================"