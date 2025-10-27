#! /bin/bash

[[ -n "${TRACE:-}" ]] && set -x

set -eu

config_has() {
    declare -r filename="$1"
    declare -r element="$2"

    grep -q \
        "<$element>\(.*\)<\/$element>" \
        "$filename"
}

config_get() {
    declare -r filename="$1"
    declare -r element="$2"

    sed -n \
        -e "s/.*<$element>\(.*\)<\/$element>.*/\1/p" \
        "$filename"
}

config_set() {
    declare -r filename="$1"
    declare -r element="$2"
    declare -r value="$3"

    sed -i \
        -e "s^<$element>.*</$element>^<$element>$value</$element>^" \
        "$filename"
}

config_append() {
    declare -r filename="$1"
    declare -r element="$2"
    declare -r value="$3"
    declare -r parent_element="${4:-config}"

    declare -r indentation="$(sed -n \
        -e "s/^\(\s*\)<\/$parent_element>.*/\1/p" \
        "$filename")"

    sed -i \
        -e "\^</$parent_element>^ i \    $indentation<$element>$value</$element>" \
        "$filename"
}

config_fix() {
    declare -r filename="$1"
    declare -r element="$2"
    declare -r value="$3"
    declare -r parent_element="${4:-config}"

    if config_has "$filename" "$element"; then
        config_set "$filename" "$element" "$value"
    else
        config_append "$filename" "$element" "$value" "$parent_element"
    fi
}

config_pass() {
    declare -r old_config="$1"
    declare -r new_config="$2"
    declare -r element="$3"
    declare -r parent_element="${4:-config}"

    if ! config_has "$old_config" "$element"; then
        return 0
    fi

    declare -r old_value="$(config_get "$old_config" "$element")"
    config_fix "$new_config" "$element" "$old_value" "$parent_element"
}

is_systemd_init() {
    [[ "$(cat "/proc/1/comm")" = "systemd" ]]
}

is_upstart_init() {
    [[ "$(/sbin/init --version 2> /dev/null)" =~ [Uu]pstart ]]
}

is_xdr_collector_installed() {
    declare -r search_dir="$1"

    if [[ ! -d "$search_dir" ]]; then
        return 1
    fi

    if [[ ! -e "$search_dir/bin/version.txt" ]]; then
        return 1
    fi

    if [[ ! -e "$search_dir/bin/xcd" ]]; then
        return 1
    fi

    if [[ ! -e "$search_dir/config/XDR_Collector.xml" ]]; then
        return 1
    fi

    return 0
}

remove_all_files() {
    declare -r local_deploy_dir="$1"
    declare -r local_panw_dir="$2"

    # Remove deploy-dir and its content
    if [[ -n "${local_deploy_dir:-}" && -d "$local_deploy_dir" ]]; then
        rm -rf "$local_deploy_dir"
    fi

    # Remove /opt/paloaltonetworks dir if empty
    if [[ -z "$(ls -A $local_panw_dir)" ]]; then
        rmdir "$local_panw_dir"
    fi
}

unregister() {
    # We don't wrap this using double quotes, as we want to expand into a list.
    declare -r -a xcd_pids=($(pidof xcd))

    if [[ "${#xcd_pids[@]}" -eq 0 ]]; then
        echo "Collector is down, skipping unregistration"
        return 0
    fi

    # Notify xcd to unregister before removal
    kill -s USR2 ${xcd_pids[@]}

    # Give the process some time to handle the signal
    sleep 5
}

load_arguments_file() {
    declare -r arguments_path="/etc/panw/collector.conf"
    if [[ ! -e "$arguments_path" ]]; then
        return 0
    fi

    owner_uid="$(stat -c "%u" "$arguments_path")"
    owner_gid="$(stat -c "%g" "$arguments_path")"
    mode="$(stat -c "%A" "$arguments_path")"
    if [[ ! -f "$arguments_path" ]]; then
        echo "Ignoring $arguments_path since not a regular file $(stat -c "%F" "$arguments_path")"
        return 0
    elif [[ "$owner_uid" -ne 0 || "$owner_gid" -ne 0 ]]; then
        echo "Ignoring $arguments_path since not owned by root (${owner_uid}:${owner_gid})"
        return 0
    elif [[ "$mode" =~ ........w. ]]; then
        echo "Ignoring $arguments_path since world-writable ($mode)"
        return 0
    fi

    cat "$arguments_path"
}

installer_arguments_usage() {
    echo "Usage: $0 -- [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  --data-path <path>, -d <path>                                    "
    echo "          Set path for collected data. ex: /var/collected          "
    echo "                                                                   "
    echo "  --proxy-list <proxies>, -x <proxies>                             "
    echo "          Set proxies for web connections. ex: 10.0.0.80;10.0.0.81 "
    echo "                                                                   "
    echo "  --dist-id <id>                                                   "
    echo "          Set the distribution id                                  "
    echo "                                                                   "
    echo "  --elb-addr <url>                                                 "
    echo "          Set the elb address                                      "
}

# Parse arguments from /etc/panw/collector.conf, and set variables to be
# used by caller.
parse_installer_arguments() {
    # Not using `declare` since it hides the return value.
    options="$(getopt --name "$0" \
        -q \
        --options "hd:x:i:a:" \
        --longoptions "help" \
        --longoptions "data-path:" \
        --longoptions "proxy-list:" \
        --longoptions "dist-id:" \
        --longoptions "elb-addr:" \
        -- "$@")"

    if [[ $? -ne 0 ]]; then
        echo "Failed parsing installer arguments $1"
        installer_arguments_usage
        return 2
    fi

    # Re-arrange positional arguments.
    eval set -- "$options"

    while true; do
        case "$1" in
            -h | --help)
                installer_arguments_usage
                return 2
                ;;

            -d | --data-path)
                data_path="$2"
                shift 2
                ;;

            -x | --proxy-list)
                proxy_list="$2"
                shift 2
                ;;

            -i | --dist-id)
                dist_id="$2"
                shift 2
                ;;

            -a | --elb-addr)
                elb_addr="$2"
                shift 2
                ;;

            --)
                shift
                break
                ;;

            *)
                echo "Invalid installer argument $1"
                installer_arguments_usage
                return 2
                ;;
        esac
    done
}

postinst() {

    declare -r deb_operation="${1:-}"
    declare -r deploy_dir="/opt/paloaltonetworks/xdr-collector"

    case "$deb_operation" in
        configure)
            # Update internal XML configuration using arguments from /etc/panw/collector.conf
            declare data_path="$deploy_dir/data"
            declare proxy_list=""
            declare dist_id=""
            declare elb_addr=""
            declare -r -a arguments=($(load_arguments_file))
            parse_installer_arguments "${arguments[@]:-}" || true

            config_set "$deploy_dir/config/XDR_Collector.xml.template" "data_path" "$data_path"
            config_set "$deploy_dir/config/XDR_Collector.xml.template" "proxy_list" "$proxy_list"
            config_set "$deploy_dir/config/XDR_Collector.xml.template" "distribution_id" "$dist_id"
            config_set "$deploy_dir/config/XDR_Collector.xml.template" "cloud_elb_address" "$elb_addr"
            if [[ ! -e "$deploy_dir/config/XDR_Collector.xml" ]]; then
                cp "$deploy_dir/config/XDR_Collector.xml.template" "$deploy_dir/config/XDR_Collector.xml"
            fi
            #rm "$deploy_dir/config/XDR_Collector.xml.template"

            # Autostart service after install
            #if is_systemd_init; then
                #echo "Systemd: starting xdr-collector service"
                #systemctl daemon-reload 2> /dev/null
                #systemctl enable xdr-collector
                #systemctl restart xdr-collector
            #elif is_upstart_init; then
                #echo "Upstart: starting xdr-collector service"
                #initctl stop xdr-collector 2> /dev/null || true
                #initctl start xdr-collector || true
            #else
                #echo "Unrecognized init system. skipping service start"
            #fi

            return 0
            ;;

        abort-upgrade | abort-remove | abort-deconfigure)
            return 0
            ;;
        *)
            echo "Unknown postinst command: $deb_operation" >&2
            return 1
            ;;
    esac
}

[[ "$0" == "$BASH_SOURCE" ]] && postinst "$@"
