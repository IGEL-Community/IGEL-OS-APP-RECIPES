# Handy — offline speech-to-text for IGEL OS 12

[Handy](https://handy.computer) ([cjpais/Handy](https://github.com/cjpais/Handy), MIT) is a free,
open-source, fully offline speech-to-text app. Press a global hotkey (default **Ctrl+Space**),
speak, release — the transcription is typed into whatever window has keyboard focus, including
remote sessions (Citrix / Omnissa Horizon / RDP / browser).

## Building the app

**One upload:** `Handy_0.9.4_amd64.deb` (~49 MB) —
[download](https://github.com/cjpais/Handy/releases/download/v0.9.4/Handy_0.9.4_amd64.deb) ·
[all releases](https://github.com/cjpais/Handy/releases) (pick the `_amd64.deb` asset,
not arm64/AppImage/rpm).

The **speech model is not packaged.** Either users pick one in Handy's own model manager,
or you put a model URL in the UMS profile and each device downloads it once into its
persistent partition (see *Supplying a speech model*). That keeps the `.ipkg` at ~70 MB
and makes the model an admin setting rather than a rebuild.

Then:

1. Zip this recipe directory (the folder contents, not the parent folder) — or use the
   CI-built `APP_Packages/Apps/handy_community.zip` after merging to `main`.
2. Upload the recipe zip and `Handy_0.9.4_amd64.deb` to the
   [IGEL App Creator Portal](https://appcreator.igel.com) and build.
3. Import the resulting `.ipkg` (~70 MB) into UMS and assign it to devices.

> **Portal upload rules — tested 2026-07-27, in case you ever want to bundle a model:**
>
> - The Portal only accepts **`tar.*`, `tgz`, `gz`, `zip`, `deb`, `bz2`** as attachments
>   (SDK manual §9.3), so a bare `.gguf` is rejected — it would have to be wrapped
>   (`tar -czf model.tar.gz model.gguf`).
> - **Every `thirdparty.json` entry needs an uploaded file, whatever its `url` says.**
>   The SDK supports `http`/`https`/`ftp` sources (§9.1.1) and the `igelpkg` CLI fetches
>   them, but the **Portal blocks the build until each entry has an attachment** — an
>   `https://` URL does not remove the upload step.
>
> This recipe deliberately bundles nothing but the `.deb`: a bundled model inflates the
> package by hundreds of MB and re-ships with every app update. For fleets without
> internet egress, host the model on an internal web server and point the profile URL at
> it — see *Air-gapped and restricted-egress fleets*.

## Supplying a speech model

Handy ships no model; a fresh install prompts the user to download one. On a managed
fleet you can skip that by setting **Speech model URL** in the UMS profile
(Handy → Dictation) to the direct download URL of a `.gguf`:

```
https://huggingface.co/handy-computer/canary-180m-flash-gguf/resolve/main/canary-180m-flash-Q8_0.gguf
```

Each device downloads that file once, in the background, into Handy's own custom-models
directory (`/userhome/.local/share/com.pais.handy/models`) — the location its startup scan
reads — saved with a `ums-` prefix (`ums-canary-180m-flash-Q8_0.gguf`). Handy registers it
as a model whose ID is that filename minus the extension, and the recipe then **selects it
explicitly**, so it wins over anything already on the device. Set **First-run onboarding =
Skip** alongside it: Handy does not auto-select anything while its wizard is still pending.

Two upstream behaviours make both of those details load-bearing, and getting them wrong is
why an earlier revision fetched a model that was then ignored:

- Handy's scan **skips a file whose name matches the default-quant filename of a catalog
  model** — the catalog already claims that name, and catalog models only count as
  downloaded when they sit in the Hugging Face cache. Without the prefix, a URL pointing at
  `canary-180m-flash-Q8_0.gguf` produces a file Handy cannot see at all.
- `auto_select_model_if_needed()` picks the first downloaded model **in catalog rank
  order**, and a dropped-in model has no rank, so it sorts last. Any model already present
  — including one left in the Hugging Face cache by an older recipe version — would be
  selected instead. Hence the explicit selection, written only once the file is on disk
  (Handy clears a selection it cannot resolve).

Because the download is asynchronous and Handy only scans for models at startup, the
model becomes active at the **next** session start (log off/on, or quit Handy from the
tray and reopen the session). Leave the field empty and the recipe touches nothing —
users download models in the app exactly as they would without this recipe.

**Where to find URLs:** [huggingface.co/handy-computer](https://huggingface.co/handy-computer)
hosts the GGUF conversions Handy's own catalog uses. Open a repo → **Files** → copy the
download link of a `.gguf`. Any `.gguf` (or `.bin`) Handy can load works, including a
copy you host yourself; the URL may point at any host the device can reach.

| Model | Size | Speed / Accuracy | Languages |
|---|---|---|---|
| **`canary-180m-flash-gguf` / `canary-180m-flash-Q8_0.gguf`** ← Handy's default quant for this model | 218 MB | **98** / 88 | EN, DE, ES, FR |
| `canary-180m-flash-gguf` / `…-Q4_K_M.gguf` — smaller and faster | 139 MB | 98 / 88 | EN, DE, ES, FR |
| `parakeet-unified-en-0.6b-gguf` / `…-Q4_K_M.gguf` | 477 MB | 79 / 90 | English |
| `parakeet-unified-en-0.6b-gguf` / `…-Q8_0.gguf` | 731 MB | 79 / 90 | English |

Speed/accuracy are Handy's own catalog scores. **On thin-client CPUs, model choice is
the dominant factor in how long a dictation takes** — Canary 180M is a third of
Parakeet's parameter count at a lighter quantization, for about two points of accuracy.
Start there and only move up if accuracy is genuinely lacking on your hardware. On the
quantizations: `Q4_K_M` is the smallest and fastest, `Q8_0` is larger and marginally
better; Handy's own default for a model is its `default_quant` in the catalog (`Q8_0` for
Canary 180M Flash), and the speed/accuracy scores are per model, not per quant. Handy's
catalog (with current scores and any newly recommended model) is
[`src-tauri/src/catalog/catalog.json`](https://github.com/cjpais/Handy/blob/main/src-tauri/src/catalog/catalog.json).

**Changing the URL later** moves the fleet: the new file is fetched, and it is selected at
the following session start. Like every other managed field, this one is admin-owned — a
user's own model choice is overridden on a managed device. Leave the field empty if users
should choose. Nothing is ever removed automatically, so each URL change leaves the
previous file behind: see *Persistence* for the disk cost.

If the download fails (bad URL, no egress), nothing breaks — the failure is logged to
systemlog, the attempt repeats at the next session start, any model already selected
keeps working, and users can still download a model in Handy's UI.

## Updating to a new Handy version

1. **New app version** — grab the new `_amd64.deb` from the releases page above, then
   bump `version` in `app.json` (`{app_version}+{igel_build}`, e.g. `0.9.5+1.0`) and add
   a `data/changelogs/en` entry. Every recipe change needs a version bump or UMS will
   not push the update.
2. **Re-check the runtime deps** — unpack the new `.deb` and compare its `Depends:` and
   the binary's `NEEDED` list against `igel/debian.json` (see *Runtime dependencies*
   below; the `libappindicator3-1` → ayatana and `libopenblas0` → `libopenblas0-pthread`
   substitutions are the ones that bite).
3. **Re-check the settings keys** the sync helper writes
   (`input/all/config/bin/handy-settings-sync.py`) against upstream
   `src-tauri/src/settings.rs` — the enum spellings (`model_unload_timeout`,
   `overlay_style`, `paste_method`, `keyboard_implementation`, `typing_tool`) are serde
   variants, and an unknown one fails Handy's whole settings load. The helper validates
   against the lists in that file, so a renamed variant shows up as
   `ignoring invalid …` in systemlog rather than a broken app.
4. Build and import as in *Building the app* — only the `.deb` is uploaded; models are
   downloaded by the devices.

Nothing else needs syncing: there are no model pins, checksums or catalog copies in the
recipe.

## How it runs on IGEL OS

- `handy0` is a normal IGEL session that starts the Handy tray application. Enable
  **Autostart** on the session in UMS so it is running from login, and set
  **Window at startup = Start hidden in tray** if users should not get a window at every
  login. The launcher deliberately does *not* pass `--start-hidden`: Handy ORs that flag
  with the setting, so hardcoding it would make the profile field unreachable.
- Handy is single-instance — opening the session again while it is running shows the main
  window (settings/model manager), so users can always reach the UI even without a tray.
- **With no UMS settings, Handy behaves exactly as it does standalone** — its own
  defaults, its own onboarding wizard, its own model manager. The recipe writes nothing.
- **With a Speech model URL set**, the device downloads that file once into Handy's
  custom-models directory (prefixed `ums-`) and the recipe selects it by ID at the session
  start after it lands. Systemlog `handy:` entries trace the download and say when the
  selection is deferred because the file is not there yet; a single-flight lock plus a
  `.partial` temp name mean two session starts cannot corrupt each other's download.
- **Models users download in the app** land in the Hugging Face cache instead; the
  session script points `HF_HOME` into the persistent app-data directory so those
  survive reboots too.
- Inference runs on CPU (ggml picks the best kernel for the endpoint's CPU, down to
  SSE4.2). The Vulkan GPU backend (`libggml-vulkan.so`, 62 MB — ~45% of the upstream
  payload) is excluded in `install.json` on purpose: ggml dlopens backends best-effort,
  IGEL images don't guarantee `libvulkan.so.1`, and thin-client GPUs don't meaningfully
  accelerate these models. On low-end endpoints prefer a small model (see
  *Supplying a speech model*).

## Persistence

All user state lives under Tauri's app-data directory and is declared persistent in
`igel/dirs.json`, so it survives reboots and firmware updates:

| Path | Contents |
|---|---|
| `/userhome/.local/share/com.pais.handy` | `settings_store.json`, `models/` (the UMS-supplied model and any added by hand), `hf/` (Hugging Face cache — models downloaded in the app), `history.db` (SQLite), `recordings/` |
| `/userhome/.config/com.pais.handy` | Tauri/WebKit per-app config |

The read-write partition is 2 GB (`compressed`, `prefer_btrfs` — the history database
is SQLite, which does not tolerate NTFS compression). **Budget it against the models in
use**, because every model lives here, not in the app partition:

- one model costs 139 MB to 731 MB — see the table above;
- **nothing is ever cleaned up automatically**: changing the profile URL, or a user
  downloading a second model in the app, adds to the total. Clear
  `…/com.pais.handy/models` and `…/com.pais.handy/hf` by hand if you cycle through
  several large models;
- history and WAV recordings share the same partition.

If users should hold several large models on device (Whisper Turbo/Large are 1.6–3 GB),
raise `rw_partition.size` in `app.json`; the SDK does not document thin provisioning, so
assume the declared size claims real disk.

## UMS profile settings

The recipe adds admin-managed settings to the UMS profile editor (Handy → Hotkeys /
Post-processing / Dictation / Interface & typing). **The recipe defines no defaults of
its own** — with every field Unmanaged, Handy starts exactly as it would without this
recipe (its own defaults, its own onboarding, its own model manager), and no settings
file is created at all.

**Every field is empty ("Unmanaged") by default and an empty field never touches user
settings**; a managed (non-empty) field is admin-owned and re-applied at every Handy
start, so profile changes reach devices that already have settings. The sync
deliberately runs **only when Handy is not already running** (a running Handy holds
settings in memory and would race an external write), so profile changes take effect at
the next real Handy start — log off/on, or quit Handy from the tray and reopen the
session.

| Field | Notes |
|---|---|
| Speech model URL | Direct URL to a `.gguf`; the device downloads it once and Handy selects it when nothing else is selected — see *Supplying a speech model* |
| First-run onboarding | Skip Handy's wizard on managed devices. **Required with a Speech model URL** — Handy auto-selects nothing while onboarding is pending |
| Transcribe / Post-process hotkey | Handy binding syntax, e.g. `ctrl+super+space`. **Must contain a normal key** — modifier-only combos (Ctrl+Win) and side-specific names (`ctrl_left`) do not work on IGEL OS; see *Hotkeys: what works* |
| Post-processing enable | Enabling also selects the built-in "Improve Transcriptions" prompt |
| Provider / Base URL / Model / API key | For the low-latency OpenAI path use provider **Custom**, base URL `https://api.openai.com/v1`, model `gpt-5.6-terra` (Handy disables model reasoning only on the Custom/OpenRouter paths). Zero-setup alternative: provider **Anthropic**, model `claude-haiku-4-5`. |
| Custom vocabulary | Comma-separated company names/jargon (replaces the user's list when managed) |
| Mute while recording / Recording sounds | Fleet-wide audio behavior |
| Unload model after idle | Handy unloads after 5 min by default; the next dictation then pays a full model reload. `Never` keeps it resident — the single best latency lever after model choice |
| Recording overlay / position | Hidden, minimal pill, or live transcription panel; top or bottom |
| Window at startup | Start in the tray instead of opening the main window. Recommended with Autostart. Handy still shows the window if it needs first-run permissions |
| Keyboard implementation / Text injection tool | Leave the backend alone — Tauri is Handy's default and the only one that works here; the field exists to repair a device switched to Handy Keys in the app. Injection tool is `xdotool` on X11 (Auto normally picks it) |
| Text insertion method | `Ctrl+V` is most compatible (incl. Citrix/Omnissa); `Direct` types char-by-char where paste is blocked; `Ctrl+Shift+V` for terminals; `None` leaves text on the clipboard |
| Trailing space | Append a space so consecutive dictations don't run together |

### A working fleet configuration

An example fleet setup — smallest/fastest speech model, post-processing on a low-latency
OpenAI-compatible endpoint:

| Field | Value |
|---|---|
| Speech model URL | `https://huggingface.co/handy-computer/canary-180m-flash-gguf/resolve/main/canary-180m-flash-Q8_0.gguf` |
| First-run onboarding | `Skip` |
| Unload model after idle | `Never — keep loaded` |
| Post-processing | `Enabled` |
| Post-processing provider | `Custom (OpenAI-compatible)` |
| Custom provider base URL | `https://api.openai.com/v1` |
| Post-processing model | `gpt-5.6-terra` (or `gpt-5.6-luna` — ~0.3 s faster, lower quality) |
| Post-processing API key | the provider API key |
| Custom vocabulary | company names/jargon, comma-separated |
| Window at startup | `Start hidden in tray` |

Leave the hotkeys Unmanaged unless Handy's defaults collide with something; leave the
audio fields Unmanaged unless you want to force them fleet-wide.

The API key is delivered via the profile (password field) and stored in the device's
persistent Handy settings, readable by that device's user — use a dedicated key with
a spend limit, not your main account key. Post-processing needs egress to the chosen
provider (e.g. `api.openai.com` or `api.anthropic.com`).

### Hotkeys: what works

**A hotkey is modifiers plus exactly one normal key.** `ctrl+space` (Handy's default),
`ctrl+shift+space`, `ctrl+super+space`, `ctrl+alt+f9` — fine. Modifiers are `ctrl`,
`shift`, `alt`, `super`.

The exact spellings matter more than they look, because the parser behind Handy's Tauri
backend (`global-hotkey`) accepts only `ALT`/`OPTION`, `CONTROL`/`CTRL`,
`COMMAND`/`CMD`/`SUPER` and `SHIFT` as modifier tokens, and its key table has no
`ControlLeft`. So **`ctrl_left+space` cannot be parsed — and an unparseable shortcut
registers nothing at all**, with nothing in the app to say why. `win+space` fails the same
way: `win`, `windows` and `meta` are not tokens that parser knows. This is worth knowing
because `ctrl_left` is exactly what Handy's own key recorder and its `handy_keys` backend
produce, so the string that works in one backend silently disables the hotkey in the other.

The recipe repairs the near-misses rather than passing them through: side-specific names
lose the side, `win`/`windows`/`meta` become `super`, and modifiers are re-emitted before
the key (that parser rejects a key that comes first). Every repair is logged:

```
handy: settings sync: normalized hotkey 'ctrl_left+space' to 'ctrl+space';
```

A combination that could not register even after that — no normal key (`ctrl+super`), more
than one, or an unknown key name — is **refused**, leaving whatever binding the user
already had, and logged as `ignoring unusable hotkey`. **Modifier-only combos such as
Ctrl+Win therefore remain impossible;** `ctrl+super+space` is the closest thing that works.

### "It dictates once, then the hotkey does nothing"

That is an upstream signal collision, not a configuration mistake, and the recipe works
around it. Handy maps **SIGUSR1** to "toggle dictation with post-processing" so it can be
driven remotely. WebKitGTK — the webview Handy's entire UI runs in — uses **the same
signal** to suspend threads for JavaScriptCore's garbage collector (`WTF`'s
`ThreadingPOSIX.cpp` sets `sigThreadSuspendResume = SIGUSR1`, and the GC's *Collector
Thread* `pthread_kill()`s the process with it every few minutes). Handy takes that for a
hotkey press and starts a recording nobody asked for. Nothing ever stops it, and while it
is active **every real push-to-talk press is ignored** — the transcription coordinator only
starts on a press when it is idle. So the app dictates once, then appears deaf until it is
restarted.

The session launcher exports `JSC_SIGNAL_FOR_GC=30`, which WebKit reads to move its GC
signal elsewhere. That removes the collision without patching Handy. Upstream tracks it as
[#1660](https://github.com/cjpais/Handy/issues/1660) with a fix proposed in
[#1267](https://github.com/cjpais/Handy/pull/1267) (unmerged); drop the export once a Handy
release no longer listens on SIGUSR1.

To confirm on a device, look for the signature in Handy's own log
(`/userhome/.local/share/com.pais.handy/logs/handy.log`, debug level by default):

```
[handy_app_lib::signal_handle][DEBUG] Received SIGUSR1
[handy_app_lib::actions][DEBUG] TranscribeAction::start called for binding: transcribe_with_post_process
```

with nobody having pressed the post-process hotkey. After this fix that pair should not
appear at all.

Handy does have a second backend, *Handy Keys*, which accepts modifier-only combos — and
the profile deliberately does **not** offer it, because on IGEL OS it silently disables
every hotkey. It reads keyboards straight from evdev and, since Handy uses its blocking
constructor, grabs each keyboard (`EVIOCGRAB`) and re-injects through `/dev/uinput`. The
session user can access neither device, and the resulting failure is invisible: it happens
inside the backend's own manager thread, `HandyKeysState::new()` has already returned `Ok`,
and `init_shortcuts()` logs and swallows every per-binding registration error, so upstream's
fallback to Tauri never fires. The app looks completely healthy with **no hotkey registered
at all** — not even Handy's own `Ctrl+Space`.

Granting that access is possible (a udev rule for keyboards plus `uinput`) but not worth it
on a thin client: it hands raw keystroke-read and event-injection capability to the desktop
user, and an exclusive keyboard grab can cost a session its keyboard entirely if X11 does
not pick up the re-injection clone. Only modifier-only hotkeys would be gained.

**If a device ends up on Handy Keys anyway** — a user can still switch backends in Handy's
own settings — it stops responding to every hotkey. Repair it by setting *Keyboard
implementation* to `Tauri` in the profile (that writes the backend back), or by switching
it back in the app. The profile field exists for exactly that; a stale `handy_keys` value
left in an older profile is ignored rather than re-applied, with an
`ignoring invalid keyboard_implementation` line in systemlog.


## Fleet / offline notes

- **The model is downloaded once per device.** It lives in the persistent partition, and
  the download starts with an existence check, so a restart never re-downloads. Only a
  new URL, or wiping the persistent partition, causes another download.
- Downloads from `huggingface.co` redirect to `cdn-lfs.huggingface.co` — allowlist both
  if devices pull from there. Handy's in-app model manager uses the same hosts.
- **In-app updates cannot work**: `/services/handy` is read-only, so ignore Handy's
  updater — upgrades ship as a new `.ipkg` built from a bumped recipe.
- **History/recordings growth**: Handy keeps WAV recordings for its transcription
  history; users can limit or clear history in Handy's settings if the partition fills.

### Air-gapped and restricted-egress fleets

The profile URL is just a URL — point it at an internal host and no device ever needs
internet access:

```bash
# on an internal web server, once
curl -L -o /var/www/html/handy/canary-180m-flash-Q8_0.gguf \
  "https://huggingface.co/handy-computer/canary-180m-flash-gguf/resolve/main/canary-180m-flash-Q8_0.gguf"
```

Then set **Speech model URL** to
`https://intranet.example.com/handy/canary-180m-flash-Q8_0.gguf`. Requirements: the
URL must end in `.gguf` (or `.bin`) — the filename is taken from the URL path — and the
server's TLS certificate must be trusted by the device (or use plain `http://` on a
trusted network). A UMS file transfer to `/wfs` also works if you prefer, but then the
model consumes `/wfs` space on every device and Handy has to be pointed at it by hand;
an internal URL is simpler and costs nothing on the endpoint.

Verify on a device via systemlog:

```
handy: downloading speech model ums-canary-180m-flash-Q8_0.gguf from https://…
handy: speech model ums-canary-180m-flash-Q8_0.gguf downloaded — Handy selects it at the next session start
```

A failure logs `speech model download failed (curl exit N)` and retries at the next
session start.

## Runtime dependencies

The upstream `.deb` declares `libappindicator3-1`, which no longer exists in Debian
Bookworm — the recipe pulls `libayatana-appindicator3-1` (plus its indicator/dbusmenu
chain; the Tauri tray dlopens either flavor). Also from Bookworm repos:

- `libgtk-layer-shell0` — linked by the binary (NEEDED) even though the overlay runs in
  regular-window mode on X11.
- `libopenblas0-pthread` + `libgfortran5` + `libquadmath0` — `libtranscribe.so.0` links
  `libopenblas.so.0`. Maintainer trap: plain `libopenblas0` is a documentation-only
  metapackage on Bookworm, and the SDK does not resolve package dependencies, so all
  three must stay listed explicitly. Loader wiring (why and how) is commented in the
  session script `input/all/config/sessions/handy0`.

Deliberately **not** bundled — `app.json` pins `base_system >= 12.5.0`, which ships the
WebKitGTK 4.1 stack (`libwebkit2gtk-4.1-0` / `libjavascriptcoregtk-4.1-0` /
`libsoup-3.0-0`), GTK3/GLib/Cairo, ALSA (`libasound2`), OpenSSL 3, and `xdotool`.
The Handy binary carries `RUNPATH=$ORIGIN/../lib/Handy`, so its bundled ggml /
onnxruntime / transcribe libraries resolve from `/services/handy/usr/lib/Handy`
without a wrapper.

The session launcher **enforces** the WebKit expectation at start: if the base image
does not expose `libwebkit2gtk-4.1`, it logs
`base system lacks libwebkit2gtk-4.1 …` to systemlog (`logger -it handy`) and exits
instead of failing silently. If that ever fires on your image, add the WebKit-stack
Bookworm packages to `igel/debian.json` and rebuild.

## Coexistence with VDI real-time audio (Omnissa Horizon, Citrix)

Microphone capture on IGEL OS goes through the sound server (PipeWire on current 12.x,
PulseAudio interface preserved), which **multiplexes capture streams** — Horizon RTAV in
a remote session and Handy on the local host can record at the same time. Handy opens
ALSA's `default` PCM, which IGEL bridges to the sound server. To verify on a device:
start Handy during an active RTAV call and check `pactl list source-outputs short`
shows two capture clients.

Practical caveats:

- **Do not USB-redirect the headset** into the VDI session — generic USB redirection
  hands the whole device to the remote VM and Handy (and everything else local) loses
  the microphone. Use RTAV for audio, and exclude headsets from Horizon USB auto-connect.
- A full-screen Horizon session can grab keyboard combos. If Ctrl+Space never reaches
  Handy, keep the combo local via Horizon's `/etc/vmware/view-keycombos-config`, or remap
  Handy's binding to a chord the client does not grab.
- Handy's recording overlay is an always-on-top window, but an X11 full-screen VDI client
  outranks that, so the overlay can sit behind a full-screen session. Set
  **Recording sounds = On** and **Recording overlay = Hidden** for those users.
- Transcribed text is injected as local keystrokes and lands in the focused window —
  typing into the remote desktop is exactly what happens.
- Local inference competes with the Blast/PCoIP decoder for CPU; prefer the smallest
  model that meets your accuracy bar (see *Supplying a speech model*).

## Hardware requirements

Upstream recommends an Intel 6th-gen (Skylake) class CPU or newer; the package ships ggml
CPU variants down to SSE4.2, so older hardware still runs (slower).
