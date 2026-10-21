#!/usr/bin/env bash
set -euo pipefail

BASEDIR=$(git rev-parse --show-toplevel)
cd "$BASEDIR"
SRCLOC="$BASEDIR/APP_Source"
ZIPLOCATION="$BASEDIR/APP_Packages"
CATEGORIES=(Apps Browsers Multimedia Network Office Scripts Server Tools_Drivers Unified_Communications)

# Compare the complete push range, not just HEAD~1. If the base commit
# is unavailable (e.g. a newly created branch), rebuild all packages.
REBUILD_ALL=false
if [[ ${BEFORE_SHA:-} =~ ^[0-9a-f]{40}$ && ${AFTER_SHA:-} =~ ^[0-9a-f]{40}$ ]] &&
   [[ $BEFORE_SHA != 0000000000000000000000000000000000000000 ]] &&
   git cat-file -e "${BEFORE_SHA}^{commit}" 2>/dev/null &&
   git cat-file -e "${AFTER_SHA}^{commit}" 2>/dev/null; then
    mapfile -d '' -t CHANGED < <(git diff --name-only -z "$BEFORE_SHA" "$AFTER_SHA" -- APP_Source/ utils/readme.txt utils/disclaimer.txt)
else
    echo "No usable push commit range; rebuilding all packages"
    REBUILD_ALL=true
    CHANGED=()
fi

printf 'Changed source files:\n'
printf '  %s\n' "${CHANGED[@]}"

COMMON_CHANGED=false
for changed in "${CHANGED[@]}"; do
    case "$changed" in
        utils/readme.txt|utils/disclaimer.txt) COMMON_CHANGED=true ;;
    esac
done

for category in "${CATEGORIES[@]}"; do
    category_dir="$SRCLOC/$category"
    [[ -d $category_dir ]] || continue
    mkdir -p "$ZIPLOCATION/$category"

    # Clean up ZIPs for removed application directories.
    for changed in "${CHANGED[@]}"; do
        case "$changed" in
            "APP_Source/$category/"*)
                remainder=${changed#"APP_Source/$category/"}
                app=${remainder%%/*}
                if [[ -n $app && ! -d "$category_dir/$app" ]]; then
                    removed_zip="$ZIPLOCATION/$category/${app}_community.zip"
                    if [[ -f $removed_zip ]]; then
                        echo "Removing package for deleted app: $category/$app"
                        rm -f "$removed_zip"
                    fi
                fi
                ;;
        esac
    done

    for app_dir in "$category_dir"/*; do
        [[ -d $app_dir ]] || continue
        app=${app_dir##*/}
        zip_file="$ZIPLOCATION/$category/${app}_community.zip"
        zip_needed=$REBUILD_ALL
        [[ -f $zip_file ]] || zip_needed=true
        [[ $COMMON_CHANGED == true ]] && zip_needed=true

        for changed in "${CHANGED[@]}"; do
            case "$changed" in
                "APP_Source/$category/$app/"*) zip_needed=true; break ;;
            esac
        done
        [[ $zip_needed == true ]] || continue

        echo "Building package: $category/$app"
        # Package all source contents directly at the archive root.
        # Exclude legacy temporary build directories named 'tmp'.
        temp_zip=$(mktemp "$ZIPLOCATION/$category/.${app}_community.XXXXXX.zip")
        rm -f "$temp_zip"
        if (cd "$app_dir" && zip -q -r "$temp_zip" . -x 'tmp/*' '*/tmp/*'); then
            mv -f "$temp_zip" "$zip_file"
        else
            rm -f "$temp_zip"
            echo "Failed to build $category/$app" >&2
            exit 1
        fi
    done
done
