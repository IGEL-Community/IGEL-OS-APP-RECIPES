#!/usr/bin/env python3
"""Apply UMS profile values to Handy's settings_store.json.

Runs at every session start (as the session user), before Handy launches.
Reads HANDY_UMS_* environment variables (exported by the session script from
/run/handy/handy.env, which handy-init.sh writes from the IGEL registry).

Rules:
- The recipe defines NO defaults of its own. Anything the admin has not set in
  the UMS profile is left entirely to Handy's own defaults.
- A UMS value that is non-empty is written into the store (managed field) and
  re-applied at every start, so profile changes reach existing devices.
- A UMS value that is empty NEVER touches the store — users keep whatever they
  set in Handy's own UI ("empty = unmanaged" house rule).
- With nothing managed and no store present, this exits without creating one:
  Handy then starts exactly as it would unmanaged.
- Writes are atomic (tmp file + os.replace) and only happen on real change.
- Handy's settings loader officially tolerates partial settings objects
  (every field has a serde default), and merges missing hotkey bindings.
"""

import copy
import json
import os
import sys
import tempfile

STORE_DIR = "/userhome/.local/share/com.pais.handy"
STORE = os.path.join(STORE_DIR, "settings_store.json")

DEFAULT_PROMPT_ID = "default_improve_transcriptions"

# Mirrors upstream ShortcutBinding defaults (settings.rs, v0.9.4) — needed only
# when a binding entry must be created from scratch in a minimal store.
BINDING_DEFAULTS = {
    "transcribe": {
        "id": "transcribe",
        "name": "Transcribe",
        "description": "Converts your speech into text.",
        "default_binding": "ctrl+space",
    },
    "transcribe_with_post_process": {
        "id": "transcribe_with_post_process",
        "name": "Transcribe with Post-Processing",
        "description": "Converts your speech into text and applies AI post-processing.",
        "default_binding": "ctrl+shift+space",
    },
}

# Mirrors upstream default_post_process_providers() (settings.rs, v0.9.4).
# Only embedded so a base-URL override can materialise the providers array in
# a store that does not carry one yet; Handy itself persists the full array
# after any user settings change, so this matches normal app behaviour.
PROVIDER_DEFAULTS = [
    {"id": "openai", "label": "OpenAI", "base_url": "https://api.openai.com/v1",
     "allow_base_url_edit": False, "models_endpoint": "/models",
     "supports_structured_output": True},
    {"id": "zai", "label": "Z.AI", "base_url": "https://api.z.ai/api/paas/v4",
     "allow_base_url_edit": False, "models_endpoint": "/models",
     "supports_structured_output": True},
    {"id": "openrouter", "label": "OpenRouter", "base_url": "https://openrouter.ai/api/v1",
     "allow_base_url_edit": False, "models_endpoint": "/models",
     "supports_structured_output": True},
    {"id": "anthropic", "label": "Anthropic", "base_url": "https://api.anthropic.com/v1",
     "allow_base_url_edit": False, "models_endpoint": "/models",
     "supports_structured_output": False},
    {"id": "groq", "label": "Groq", "base_url": "https://api.groq.com/openai/v1",
     "allow_base_url_edit": False, "models_endpoint": "/models",
     "supports_structured_output": False},
    {"id": "cerebras", "label": "Cerebras", "base_url": "https://api.cerebras.ai/v1",
     "allow_base_url_edit": False, "models_endpoint": "/models",
     "supports_structured_output": True},
    {"id": "bedrock_mantle", "label": "AWS Bedrock (Mantle)",
     "base_url": "https://bedrock-mantle.us-east-1.api.aws/v1",
     "allow_base_url_edit": False, "models_endpoint": "/models",
     "supports_structured_output": True},
    {"id": "custom", "label": "Custom", "base_url": "http://localhost:11434/v1",
     "allow_base_url_edit": True, "models_endpoint": "/models",
     "supports_structured_output": False},
]

VALID_PROVIDERS = {p["id"] for p in PROVIDER_DEFAULTS}


def env(name):
    return os.environ.get(name, "").strip()


def as_bool(value):
    return value.lower() in ("true", "1", "yes", "on")


def set_binding(settings, binding_id, combo):
    bindings = settings.setdefault("bindings", {})
    entry = bindings.get(binding_id)
    if not isinstance(entry, dict):
        defaults = BINDING_DEFAULTS[binding_id]
        entry = dict(defaults, current_binding=defaults["default_binding"])
        bindings[binding_id] = entry
    entry["current_binding"] = combo


# Modifier spellings accepted by the parser behind Handy's Tauri backend
# (global-hotkey's parse_hotkey), mapped from every spelling an admin might
# reasonably type. Note what that parser does NOT accept: side-specific names
# like ctrl_left (which Handy's own key recorder and its handy_keys backend do
# emit), and win/windows/meta for the Super key. Either one makes the whole
# shortcut unparseable, and an unparseable shortcut registers nothing at all —
# no hotkey, and nothing in the app to say why.
TAURI_MODIFIERS = {
    "ctrl": "ctrl", "control": "ctrl",
    "alt": "alt", "option": "alt",
    "shift": "shift",
    "super": "super", "meta": "super", "win": "super", "windows": "super",
    "cmd": "super", "command": "super",
}

# Main keys that parser accepts, lowercased (global-hotkey 0.7 parse_key).
TAURI_KEYS = frozenset("""
    space tab enter escape esc backspace delete insert home end pageup pagedown
    up down left right arrowup arrowdown arrowleft arrowright
    capslock numlock scrolllock printscreen pause pausebreak
    backquote backslash bracketleft bracketright comma equal minus period quote
    semicolon slash
    a b c d e f g h i j k l m n o p q r s t u v w x y z
    keya keyb keyc keyd keye keyf keyg keyh keyi keyj keyk keyl keym keyn keyo
    keyp keyq keyr keys keyt keyu keyv keyw keyx keyy keyz
    0 1 2 3 4 5 6 7 8 9
    digit0 digit1 digit2 digit3 digit4 digit5 digit6 digit7 digit8 digit9
    f1 f2 f3 f4 f5 f6 f7 f8 f9 f10 f11 f12 f13 f14 f15 f16 f17 f18 f19 f20 f21
    f22 f23 f24
    num0 num1 num2 num3 num4 num5 num6 num7 num8 num9 numadd numdecimal
    numdivide numenter numequal nummultiply numplus numsubtract
    numpad0 numpad1 numpad2 numpad3 numpad4 numpad5 numpad6 numpad7 numpad8
    numpad9 numpadadd numpaddecimal numpaddivide numpadenter numpadequal
    numpadmultiply numpadplus numpadsubtract
    audiovolumeup audiovolumedown audiovolumemute volumeup volumedown volumemute
    mediaplay mediapause mediaplaypause mediastop mediatracknext
    mediatrackprev mediatrackprevious
""".split())


def normalize_shortcut(raw):
    """Rewrite a hotkey into the form Handy's Tauri backend can register.

    Drops `_left`/`_right` from modifier names and maps win/windows/meta onto
    super, then re-emits modifiers first (that parser rejects a key before a
    modifier). Returns None when the result could not register anyway — no
    normal key, more than one, or a key name the parser does not know — so the
    caller can leave the user's working binding alone and say why.
    """
    mods, keys = [], []
    for part in (p.strip().lower() for p in raw.split("+")):
        if not part:
            continue
        base = part
        if base.endswith(("_left", "_right")):
            stem = base.rsplit("_", 1)[0]
            if stem in TAURI_MODIFIERS:
                base = stem
        if base in TAURI_MODIFIERS:
            mod = TAURI_MODIFIERS[base]
            if mod not in mods:
                mods.append(mod)
        else:
            keys.append(base)
    if len(keys) != 1 or keys[0] not in TAURI_KEYS:
        return None
    return "+".join(mods + keys)


def main():
    managed = any(env(v) for v in (
        "HANDY_UMS_TRANSCRIBE_HOTKEY", "HANDY_UMS_POSTPROCESS_HOTKEY",
        "HANDY_UMS_POSTPROCESS_ENABLED", "HANDY_UMS_POSTPROCESS_PROVIDER",
        "HANDY_UMS_POSTPROCESS_BASE_URL", "HANDY_UMS_POSTPROCESS_MODEL",
        "HANDY_UMS_POSTPROCESS_API_KEY", "HANDY_UMS_CUSTOM_WORDS",
        "HANDY_UMS_MUTE_WHILE_RECORDING", "HANDY_UMS_AUDIO_FEEDBACK",
        "HANDY_UMS_SKIP_ONBOARDING", "HANDY_UMS_MODEL_UNLOAD_TIMEOUT",
        "HANDY_UMS_OVERLAY_STYLE", "HANDY_UMS_OVERLAY_POSITION",
        "HANDY_UMS_PASTE_METHOD", "HANDY_UMS_APPEND_TRAILING_SPACE",
        "HANDY_UMS_KEYBOARD_IMPL", "HANDY_UMS_TYPING_TOOL",
        "HANDY_UMS_START_HIDDEN", "HANDY_UMS_MODEL_ID",
    ))

    fresh = not os.path.isfile(STORE)
    if fresh and not managed:
        # Nothing to manage and no store yet — leave Handy to its own defaults.
        print("unmanaged")
        return 0
    if fresh:
        store = {"settings": {}}
    else:
        try:
            with open(STORE, encoding="utf-8") as fh:
                store = json.load(fh)
        except (OSError, ValueError) as exc:
            print(f"unreadable settings store, leaving untouched: {exc}",
                  file=sys.stderr)
            return 1
    settings = store.setdefault("settings", {})
    before = copy.deepcopy(store)

    # --- first-run onboarding ---
    # Only ever set to true. Writing false on an existing store would reset a
    # wizard the user already completed, re-showing it on every start.
    if as_bool(env("HANDY_UMS_SKIP_ONBOARDING")):
        settings["onboarding_completed"] = True

    # --- speech model ---
    # The session script sets this only once the model file is on disk, so the
    # ID always resolves. Selecting explicitly is required: a dropped-in model
    # has no catalog rank, so Handy's own auto-selection prefers any other
    # downloaded model over it.
    model_id = env("HANDY_UMS_MODEL_ID")
    if model_id:
        settings["selected_model"] = model_id

    # --- hotkeys ---
    for var, binding_id in (
        ("HANDY_UMS_TRANSCRIBE_HOTKEY", "transcribe"),
        ("HANDY_UMS_POSTPROCESS_HOTKEY", "transcribe_with_post_process"),
    ):
        raw = env(var)
        if not raw:
            continue
        combo = normalize_shortcut(raw)
        if combo is None:
            print(f"ignoring unusable hotkey '{raw}' for {binding_id}: needs "
                  "modifiers plus exactly one normal key, e.g. ctrl+space",
                  file=sys.stderr)
            continue
        if combo != raw.strip():
            print(f"normalized hotkey '{raw}' to '{combo}'", file=sys.stderr)
        set_binding(settings, binding_id, combo)

    # --- post-processing ---
    pp_enabled = env("HANDY_UMS_POSTPROCESS_ENABLED")
    if pp_enabled:
        settings["post_process_enabled"] = as_bool(pp_enabled)
        if as_bool(pp_enabled):
            settings["experimental_enabled"] = True
            # A full Handy store carries an explicit null here, which
            # setdefault() would preserve — upstream then skips
            # post-processing entirely. Replace null/empty, keep a real
            # user selection.
            if not settings.get("post_process_selected_prompt_id"):
                settings["post_process_selected_prompt_id"] = DEFAULT_PROMPT_ID

    provider = env("HANDY_UMS_POSTPROCESS_PROVIDER")
    if provider:
        if provider in VALID_PROVIDERS:
            settings["post_process_provider_id"] = provider
        else:
            print(f"ignoring unknown post-process provider '{provider}'",
                  file=sys.stderr)
            provider = ""

    model = env("HANDY_UMS_POSTPROCESS_MODEL")
    if model:
        if provider:
            settings.setdefault("post_process_models", {})[provider] = model
        else:
            print("post-processing model configured without a provider — ignored",
                  file=sys.stderr)

    api_key = env("HANDY_UMS_POSTPROCESS_API_KEY")
    if api_key:
        if provider:
            settings.setdefault("post_process_api_keys", {})[provider] = api_key
        else:
            print("post-processing API key configured without a provider — ignored",
                  file=sys.stderr)

    base_url = env("HANDY_UMS_POSTPROCESS_BASE_URL")
    if base_url and provider == "custom":
        providers = settings.get("post_process_providers")
        if not isinstance(providers, list) or not providers:
            providers = copy.deepcopy(PROVIDER_DEFAULTS)
            settings["post_process_providers"] = providers
        custom = next((e for e in providers if e.get("id") == "custom"), None)
        if custom is None:
            # Older/partial stores can carry a providers array without the
            # custom entry — append the upstream default before overriding.
            custom = copy.deepcopy(PROVIDER_DEFAULTS[-1])
            providers.append(custom)
        custom["base_url"] = base_url

    # --- dictation extras ---
    words = env("HANDY_UMS_CUSTOM_WORDS")
    if words:
        settings["custom_words"] = [w.strip() for w in words.split(",")
                                    if w.strip()]
    mute = env("HANDY_UMS_MUTE_WHILE_RECORDING")
    if mute:
        settings["mute_while_recording"] = as_bool(mute)
    feedback = env("HANDY_UMS_AUDIO_FEEDBACK")
    if feedback:
        settings["audio_feedback"] = as_bool(feedback)

    # --- behaviour / interface ---
    # Enum values are Handy's own serde spellings (settings.rs): ModelUnloadTimeout
    # snake_case, OverlayStyle/OverlayPosition lowercase, PasteMethod snake_case.
    # Validated here so a bad profile value cannot corrupt the store — Handy
    # fails the whole settings load on an unknown enum variant.
    for var, key, allowed in (
        ("HANDY_UMS_MODEL_UNLOAD_TIMEOUT", "model_unload_timeout",
         {"never", "immediately", "min2", "min5", "min10", "min15", "hour1"}),
        ("HANDY_UMS_OVERLAY_STYLE", "overlay_style",
         {"none", "minimal", "live"}),
        ("HANDY_UMS_OVERLAY_POSITION", "overlay_position",
         {"top", "bottom"}),
        ("HANDY_UMS_PASTE_METHOD", "paste_method",
         {"ctrl_v", "direct", "none", "shift_insert", "ctrl_shift_v"}),
        # handy_keys deliberately absent: it needs raw evdev + /dev/uinput
        # access the session user does not have, and fails silently (see
        # README). A stale profile value is ignored rather than re-applied.
        ("HANDY_UMS_KEYBOARD_IMPL", "keyboard_implementation",
         {"tauri"}),
        ("HANDY_UMS_TYPING_TOOL", "typing_tool",
         {"auto", "wtype", "kwtype", "dotool", "ydotool", "xdotool"}),
    ):
        value = env(var)
        if not value:
            continue
        if value in allowed:
            settings[key] = value
        else:
            print(f"ignoring invalid {key} '{value}'", file=sys.stderr)

    start_hidden = env("HANDY_UMS_START_HIDDEN")
    if start_hidden:
        settings["start_hidden"] = as_bool(start_hidden)

    trailing = env("HANDY_UMS_APPEND_TRAILING_SPACE")
    if trailing:
        settings["append_trailing_space"] = as_bool(trailing)

    if store == before and not fresh:
        print("unchanged")
        return 0
    if fresh and not settings:
        # Everything managed was rejected (e.g. a stale enum value) — creating an
        # empty store would be pointless, so leave Handy to its own defaults.
        print("unmanaged")
        return 0

    os.makedirs(STORE_DIR, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".settings_store.", dir=STORE_DIR)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(store, fh)
            fh.write("\n")
        os.replace(tmp, STORE)
    except OSError as exc:
        try:
            os.unlink(tmp)
        except OSError:
            # Best-effort cleanup of the temp file; the original write error
            # below is the one worth reporting.
            pass
        print(f"failed to write settings store: {exc}", file=sys.stderr)
        return 1
    print("seeded" if fresh else "updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
