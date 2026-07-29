#!/bin/bash
# Reads Handy's UMS profile parameters from the IGEL registry and writes an
# env file for the session launcher. Runs as root at boot and on profile
# changes (node_action restarts this service).
#
# The env file lives under root-owned /run/handy (never /tmp — an
# unprivileged user could pre-plant a symlink there and have root write
# through it), is built as a root-created temp file and atomically renamed,
# and ends up root:users 0640: the session user can read it, nobody but root
# can write it. It can carry an API key.

ACTION="handy_${1}"
LOGGER="logger -it handy-init"

echo "Starting" | $LOGGER

set -e
RUNDIR="/run/handy"
CONF="${RUNDIR}/handy.env"
install -d -m 755 -o root -g root "${RUNDIR}"
TMP=$(mktemp "${RUNDIR}/.handy.env.XXXXXX")

V() { getsysvalue "app.handy.config.$1" 2>/dev/null || true; }

{
    printf 'export HANDY_UMS_TRANSCRIBE_HOTKEY=%q\n'    "$(V transcribe_hotkey)"
    printf 'export HANDY_UMS_POSTPROCESS_HOTKEY=%q\n'   "$(V postprocess_hotkey)"
    printf 'export HANDY_UMS_POSTPROCESS_ENABLED=%q\n'  "$(V postprocess_enabled)"
    printf 'export HANDY_UMS_POSTPROCESS_PROVIDER=%q\n' "$(V postprocess_provider)"
    printf 'export HANDY_UMS_POSTPROCESS_BASE_URL=%q\n' "$(V postprocess_base_url)"
    printf 'export HANDY_UMS_POSTPROCESS_MODEL=%q\n'    "$(V postprocess_model)"
    printf 'export HANDY_UMS_POSTPROCESS_API_KEY=%q\n'  "$(V postprocess_api_key)"
    printf 'export HANDY_UMS_MODEL_URL=%q\n'            "$(V model_url)"
    printf 'export HANDY_UMS_SKIP_ONBOARDING=%q\n'      "$(V skip_onboarding)"
    printf 'export HANDY_UMS_CUSTOM_WORDS=%q\n'         "$(V custom_words)"
    printf 'export HANDY_UMS_MUTE_WHILE_RECORDING=%q\n' "$(V mute_while_recording)"
    printf 'export HANDY_UMS_AUDIO_FEEDBACK=%q\n'       "$(V audio_feedback)"
    printf 'export HANDY_UMS_MODEL_UNLOAD_TIMEOUT=%q\n' "$(V model_unload_timeout)"
    printf 'export HANDY_UMS_START_HIDDEN=%q\n'         "$(V start_hidden)"
    printf 'export HANDY_UMS_OVERLAY_STYLE=%q\n'        "$(V overlay_style)"
    printf 'export HANDY_UMS_OVERLAY_POSITION=%q\n'     "$(V overlay_position)"
    printf 'export HANDY_UMS_KEYBOARD_IMPL=%q\n'        "$(V keyboard_implementation)"
    printf 'export HANDY_UMS_TYPING_TOOL=%q\n'          "$(V typing_tool)"
    printf 'export HANDY_UMS_PASTE_METHOD=%q\n'         "$(V paste_method)"
    printf 'export HANDY_UMS_APPEND_TRAILING_SPACE=%q\n' "$(V append_trailing_space)"
} > "${TMP}"
chown root:100 "${TMP}"
chmod 640 "${TMP}"
mv -f "${TMP}" "${CONF}"

echo "Finished" | $LOGGER
