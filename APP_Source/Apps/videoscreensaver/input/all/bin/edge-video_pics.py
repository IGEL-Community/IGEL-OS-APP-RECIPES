#!/usr/bin/env python3
"""
Video + Picture Screensaver for IGEL OS 12

- Plays local videos and pictures in fullscreen kiosk/app mode via Microsoft Edge + local HTTP server
- Starts after configurable idle time (or forced start with env override)
- On user interaction, shows PIN dialog via Zenity

Pictures:
- Stored in /userhome/videoscreensaver/pics (configurable via variable)
- Shown fullscreen for PIC_SECONDS seconds (default 5)
- Served via /media.json combined playlist with videos
- Respects PLAY_ORDER = Random or By Filename

External mode (Disabled in this version):
- If EXTERNAL_WEBSERVER_ENABLED == true and EXTERNAL_URL is a valid http(s) URL,
  Edge will play external content instead of local playlist.

Dependencies: microsoft-edge (stable), zenity, xdotool, xprintidle, xinput, xset, xmodmap, setxkbmap
"""

import os
import sys
import time
import random
import subprocess
import signal
import datetime
import logging
import shutil
from pathlib import Path
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import queue
import json
from urllib.parse import urlparse


# -------------------------------
# Shell helpers (safe)
# -------------------------------
def sh(cmd: str) -> str:
    """Run a shell command and return stripped stdout as string. Raises on failure."""
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def sh_try(cmd: str, default: str = "") -> str:
    """Run a shell command; return default if it fails."""
    try:
        return sh(cmd)
    except Exception:
        return default


def sh_bool(cmd: str, default: bool = False) -> bool:
    """Read a bool from a 'get ...' command output that returns True/False."""
    try:
        out = subprocess.check_output(cmd.split(), text=True).strip()
        if out.lower() == "true":
            return True
        if out.lower() == "false":
            return False
        return default
    except Exception:
        return default


def sh_int(cmd: str, default: int = 0) -> int:
    try:
        return int(sh_try(cmd, str(default)))
    except Exception:
        return default


def valid_http_url(url: str) -> bool:
    try:
        p = urlparse((url or "").strip())
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


# -------------------------------
# Configuration
# -------------------------------
CONFIG = {
    "VIDEO_DIR": "/userhome/videoscreensaver/",
    # NEW: picture storage path
    "PICS_DIR": "/userhome/videoscreensaverpics",
    # NEW: picture duration seconds (default 5)
    "PIC_SECONDS": sh_int("get app.videoscreensaver.options.pic_seconds", default=5),

    "PIN_ENABLED": sh_bool("get app.videoscreensaver.options.pin_enabled", default=False),
    "PIN_CODE": sh_try("get app.videoscreensaver.options.pin_code", default="1234"),
    "IDLE_SECONDS": sh_int("get app.videoscreensaver.options.idle_seconds", default=300),
    "PLAY_ORDER": sh_try("get app.videoscreensaver.options.play_order", default="By Filename"),

    "LOGGING_ENABLED": sh_bool("get app.videoscreensaver.options.logging_enabled", default=True),
    "LOG_DIR": "/var/log/user/",
    "ALWAYS_START": False,

    # External mode
#    "EXTERNAL_WEBSERVER_ENABLED": sh_bool(
#        "get app.videoscreensaver.options.useexternalurl", default=False
#    ),
#    "EXTERNAL_URL": sh_try(
#        "get app.videoscreensaver.options.externalurl", default=""
#    ),
}


def is_random_order() -> bool:
    return CONFIG.get("PLAY_ORDER", "").strip().lower() == "random"


def external_mode_enabled() -> bool:
    """External mode is enabled only if flag is true AND URL is valid."""
    if not CONFIG.get("EXTERNAL_WEBSERVER_ENABLED", False):
        return False
    url = (CONFIG.get("EXTERNAL_URL") or "").strip()
    return valid_http_url(url)


# -------------------------------
# Logging setup
# -------------------------------
def setup_logging():
    if not CONFIG["LOGGING_ENABLED"]:
        return None
    Path(CONFIG["LOG_DIR"]).mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = os.path.join(CONFIG["LOG_DIR"], f"video-screensaver{ts}.log")
    logger = logging.getLogger("screensaver")
    logger.setLevel(logging.DEBUG if CONFIG.get("DEBUG") else logging.INFO)

    fh = logging.FileHandler(log_path)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh_stream = logging.StreamHandler(sys.stdout)
    sh_stream.setFormatter(fmt)
    logger.addHandler(sh_stream)

    logger.info("Logging initialized: %s", log_path)
    return logger


LOGGER = setup_logging()


def log(level, msg, *args):
    if LOGGER:
        getattr(LOGGER, level)(msg, *args)
    else:
        print(f"[{level.upper()}] " + (msg % args if args else msg))


# -------------------------------
# Wait for X
# -------------------------------
def wait_for_x(max_tries=20, sleep_s=0.5):
    """Wait until X is responding. Prevents early boot races where xinput/xset fail."""
    os.environ.setdefault("DISPLAY", ":0")
    for _ in range(max_tries):
        try:
            subprocess.check_output(["xset", "q"], stderr=subprocess.DEVNULL)
            return True
        except Exception:
            time.sleep(sleep_s)
    return False


# -------------------------------
# Idle time
# -------------------------------
def system_idle_seconds():
    """Return system idle time in seconds using xprintidle."""
    try:
        out = subprocess.check_output(["xprintidle"], timeout=1).decode().strip()
        return int(out) / 1000.0  # ms -> seconds
    except Exception:
        return 0.0


def idle_dropped(prev_idle, curr_idle, threshold=1.0):
    """Did idle reset sharply?"""
    return prev_idle > threshold and curr_idle < threshold


# -------------------------------
# XI2 root input listener with event typing
# -------------------------------
event_queue = queue.Queue()


def input_event_listener():
    """
    Input listener using XI2 root events.
    We parse event types and push (timestamp, kind) into queue.
    kinds: "key", "button", "touch", "motion"
    """
    try:
        if not wait_for_x():
            log("warning", "X not ready for input monitoring; relying on idle fallback.")
            while True:
                time.sleep(1)

        if shutil.which("xinput"):
            try:
                proc = subprocess.Popen(
                    ["xinput", "test-xi2", "--root"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    bufsize=1,
                )
                log("info", "Using xinput test-xi2 --root for input monitoring.")

                while True:
                    line = proc.stdout.readline()
                    if not line:
                        continue
                    l = line.lower()

                    kind = None
                    if "keypress" in l or "keyrelease" in l:
                        kind = "key"
                    elif "buttonpress" in l or "buttonrelease" in l:
                        kind = "button"
                    elif "touch" in l:
                        kind = "touch"
                    elif "motion" in l:
                        kind = "motion"

                    if kind:
                        event_queue.put((time.time(), kind))

            except Exception as e:
                log("warning", "xinput test-xi2 not available; falling back. %s", e)
        else:
            log("warning", "xinput not found; relying on idle fallback.")

        while True:
            time.sleep(1)

    except Exception as e:
        try:
            log("error", "Input event listener failed: %s", e)
        except Exception:
            print(f"[ERROR] Input event listener failed: {e}")


def drain_events():
    """Drain queue and return list of (ts, kind)."""
    evs = []
    while not event_queue.empty():
        try:
            evs.append(event_queue.get_nowait())
        except queue.Empty:
            break
    return evs


threading.Thread(target=input_event_listener, daemon=True).start()
log("info", "Input event listener started.")


# -------------------------------
# Confirmed interaction logic (debounced + type-aware)
# -------------------------------
def confirmed_interaction(armed, prev_idle, curr_idle, pending_motion):
    """
    Return (did_interact, new_pending_motion).

    Rules:
      - key/button/touch events => immediate interaction when armed
      - motion events are weak:
           require 3 motion events within 0.7s
           AND prev_idle > 2s
    """
    if not armed:
        drain_events()
        return (False, None)

    events = drain_events()

    # Strong evidence
    if any(k in ("key", "button", "touch") for _, k in events):
        return (True, None)

    # Weak evidence: motion
    motion_ts = [ts for ts, k in events if k == "motion"]
    now = time.time()

    if pending_motion:
        motion_ts = pending_motion + motion_ts

    motion_ts = [ts for ts in motion_ts if now - ts <= 0.7]

    if len(motion_ts) >= 3 and prev_idle > 2.0:
        return (True, None)

    return (False, motion_ts if motion_ts else None)


# -------------------------------
# Media discovery
# -------------------------------
def list_video_files():
    vid_dir = Path(CONFIG["VIDEO_DIR"])
    if not vid_dir.exists():
        log("warning", "Video directory does not exist: %s", vid_dir)
        return []
    exts = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".mpg", ".mpeg"}
    return [p for p in vid_dir.rglob("*") if p.is_file() and p.suffix.lower() in exts]


def list_pic_files():
    pics_dir = Path(CONFIG["PICS_DIR"])
    if not pics_dir.exists():
        # Not a hard error; just means no pics
        log("info", "Pictures directory does not exist: %s", pics_dir)
        return []
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    return [p for p in pics_dir.rglob("*") if p.is_file() and p.suffix.lower() in exts]


def list_media_items():
    """
    Returns list of dicts: {"type": "video"|"image", "name": "<relative-url>"}

    We serve items via the HTTP server using /v/... and /p/... prefixes so paths can differ.
    """
    vid_dir = Path(CONFIG["VIDEO_DIR"])
    pics_dir = Path(CONFIG["PICS_DIR"])

    vids = list_video_files()
    pics = list_pic_files()

    if is_random_order():
        mixed = ([{"type": "video", "path": p} for p in vids] +
                 [{"type": "image", "path": p} for p in pics])
        random.shuffle(mixed)
    else:
        mixed = sorted(
            ([{"type": "video", "path": p} for p in vids] +
             [{"type": "image", "path": p} for p in pics]),
            key=lambda item: item["path"].name.lower()
        )

    out = []
    for item in mixed:
        p = item["path"]
        if item["type"] == "video":
            try:
                rel = p.relative_to(vid_dir)
            except Exception:
                rel = p.name
            out.append({"type": "video", "name": "v/" + str(rel)})
        else:
            try:
                rel = p.relative_to(pics_dir)
            except Exception:
                rel = p.name
            out.append({"type": "image", "name": "p/" + str(rel)})

    log("info", "Found %d media items (videos=%d, pics=%d, order=%s, pic_seconds=%s)",
        len(out), len(vids), len(pics), CONFIG["PLAY_ORDER"], CONFIG["PIC_SECONDS"])
    return out


# -------------------------------
# PIN dialog via Zenity
# -------------------------------
def keep_zenity_on_top(title="Unlock Screensaver"):
    try:
        ids = subprocess.check_output(["xdotool", "search", "--name", title]).decode().split()
        for wid in ids:
            subprocess.run(["xdotool", "windowraise", wid], check=False)
            subprocess.run(["xdotool", "windowfocus", wid], check=False)
            subprocess.run(["xdotool", "windowactivate", wid], check=False)
    except subprocess.CalledProcessError:
        pass


def pin_dialog(expected_pin="1234", timeout_s=30):
    """
    - Wrong PIN => show error dialog then re-prompt.
    - Timeout => close and return False.
    - Always stays on top of Edge.
    """
    kb_id = None

    def run_zenity_on_top(cmd, title):
        raiser_stop = threading.Event()

        def raiser_loop():
            while not raiser_stop.is_set():
                keep_zenity_on_top(title)
                time.sleep(0.2)

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        raiser_thread = threading.Thread(target=raiser_loop, daemon=True)
        raiser_thread.start()

        try:
            out, _ = proc.communicate(timeout=timeout_s if "--password" in cmd else None)
        except subprocess.TimeoutExpired:
            proc.kill()
            raiser_stop.set()
            raiser_thread.join(timeout=1)
            return -9, ""
        finally:
            raiser_stop.set()
            raiser_thread.join(timeout=1)

        return proc.returncode, (out or "").strip()

    try:
        if not shutil.which("zenity"):
            log("error", "Zenity not found; cannot show PIN dialog.")
            return False

        # Disable keyboard device (existing hardening)
        try:
            kb_id = subprocess.check_output(
                "xinput list | grep -i 'keyboard' | head -n1 | awk '{print $6}' | cut -d= -f2",
                shell=True,
            ).decode().strip()
            if kb_id:
                subprocess.run(["xinput", "disable", kb_id], check=False)
                log("info", "Disabled keyboard device %s", kb_id)
        except Exception as e:
            log("warning", "Could not disable keyboard: %s", e)

        prompt_text = "Enter PIN to unlock screensaver"

        while True:
            rc, pin = run_zenity_on_top(
                [
                    "zenity",
                    "--password",
                    f"--text={prompt_text}",
                    "--title=Unlock Screensaver",
                    "--modal",
                ],
                "Unlock Screensaver",
            )

            if rc == -9:
                log("info", "PIN dialog timed out after %ss.", timeout_s)
                return False
            if rc != 0:
                log("info", "PIN dialog cancelled/closed.")
                return False

            if pin == expected_pin:
                return True

            run_zenity_on_top(
                [
                    "zenity",
                    "--error",
                    "--no-wrap",
                    "--text=Incorrect PIN, try again.",
                    "--title=Unlock Screensaver",
                    "--timeout=3",
                ],
                "Unlock Screensaver",
            )

            prompt_text = "Enter PIN to unlock screensaver"

    except Exception as e:
        log("error", "PIN dialog failed: %s", e)
        return False

    finally:
        if kb_id:
            subprocess.run(["xinput", "enable", kb_id], check=False)
            log("info", "Re-enabled keyboard device %s", kb_id)


def disable_ctrl_esc():
    subprocess.run(["xmodmap", "-e", "keycode 9 ="], check=False)
    log("info", "Disabled Escape key temporarily")


def enable_ctrl_esc():
    subprocess.run(["setxkbmap"], check=False)
    log("info", "Restored Escape key mapping")


# -------------------------------
# HTTP Handler (includes dynamic /media.json)
# -------------------------------
class VideoHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/media.json":
            try:
                items = list_media_items()
                payload = json.dumps(items).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except Exception as e:
                log("warning", "Failed to build media.json: %s", e)
                self.send_response(500)
                self.end_headers()
            return

        if parsed.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if parsed.path in ("", "/"):
            self.path = "/screensaver_playlist.html"

        return super().do_GET()

    def translate_path(self, path):
        normalized = path.lstrip("/").split("?", 1)[0]

        if normalized == "screensaver_playlist.html" or normalized == "":
            return "/tmp/screensaver_playlist.html"

        # Serve videos from VIDEO_DIR via /v/...
        if normalized.startswith("v/"):
            rel = normalized[2:]
            real_path = os.path.join(CONFIG["VIDEO_DIR"], rel)
            if os.path.isfile(real_path):
                return real_path

        # Serve pictures from PICS_DIR via /p/...
        if normalized.startswith("p/"):
            rel = normalized[2:]
            real_path = os.path.join(CONFIG["PICS_DIR"], rel)
            if os.path.isfile(real_path):
                return real_path

        return super().translate_path(path)

    def log_message(self, format, *args):
        if "favicon.ico" in str(args):
            return
        super().log_message(format, *args)


# -------------------------------
# EdgePlayer (external mode OR local playlist mode)
# -------------------------------
class EdgePlayer:
    def __init__(self):
        self.proc = None
        self.playlist_html = "/tmp/screensaver_playlist.html"
        self.http_server = None
        self.http_server_thread = None
        self.profile_dir = "/tmp/edge-screensaver-profile"
        self.edge_path = "/services/edge/opt/microsoft/msedge/microsoft-edge"

    def generate_playlist(self):
        """Generate HTML for combined video+picture playback driven by /media.json."""
        try:
            random_start = "true" if is_random_order() else "false"
            pic_seconds = int(CONFIG.get("PIC_SECONDS", 5))

            with open(self.playlist_html, "w") as f:
                f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="google" content="notranslate">
<title>Media Screensaver</title>
<style>
  html,body{{margin:0;padding:0;width:100%;height:100%;background:#000;overflow:hidden;cursor:none;}}
  .layer{{position:fixed;inset:0;width:100%;height:100%;background:#000;}}
  video, img{{width:100%;height:100%;object-fit:contain;background:#000;opacity:1;transition: opacity 1s linear;}}
  .fadeout {{ opacity:0; }}
  #img {{ display:none; }}
  #v {{ display:none; }}
  .msg{{position:fixed; top:20px; left:0; right:0;text-align:center; color:#ff0000;font-size:28px; font-weight:bold;display:none;font-family:sans-serif;}}
</style>
</head>
<body>
<div id="msg" class="msg">No media found for playback</div>

<div class="layer">
  <video id="v" autoplay muted playsinline></video>
  <img id="img" alt="">
</div>

<script>
let items = [];
let i = 0;
let lastPlayed = -1;

let deck = [];
let playlistSig = "";

const vid = document.getElementById('v');
const img = document.getElementById('img');
const msg = document.getElementById('msg');

const RANDOM_START = {random_start};
const PIC_SECONDS = {pic_seconds} * 1000;

let imageTimer = null;

function wait(ms){{ return new Promise(r => setTimeout(r, ms)); }}

function shuffleArray(arr){{
  for (let j = arr.length - 1; j > 0; j--) {{
    const k = Math.floor(Math.random() * (j + 1));
    [arr[j], arr[k]] = [arr[k], arr[j]];
  }}
}}

function rebuildDeck() {{
  deck = Array.from({{length: items.length}}, (_, idx) => idx);
  shuffleArray(deck);

  if (items.length > 1 && deck[0] === lastPlayed) {{
    const swapWith = 1 + Math.floor(Math.random() * (deck.length - 1));
    [deck[0], deck[swapWith]] = [deck[swapWith], deck[0]];
  }}
}}

function clearImageTimer() {{
  if (imageTimer) {{
    clearTimeout(imageTimer);
    imageTimer = null;
  }}
}}

async function refreshPlaylist(){{
  try{{
    const res = await fetch('/media.json?ts=' + Date.now(), {{cache:'no-store'}});
    const list = await res.json();

    const newSig = list.map(x => x.type + ":" + x.name).join("|");
    items = list;

    if(!items.length){{
      msg.style.display = 'block';
      vid.style.display = 'none';
      img.style.display = 'none';
      deck = [];
      playlistSig = "";
    }} else {{
      msg.style.display = 'none';

      if (newSig !== playlistSig) {{
        playlistSig = newSig;
        rebuildDeck();
      }}

      if(i >= items.length) i = 0;
    }}
  }}catch(e){{
    // keep old list/deck
  }}
}}

function pickNextIndex(){{
  if(!RANDOM_START){{
    return (i + 1) % (items.length || 1);
  }}

  if (items.length <= 1) {{
    deck = [0];
    return 0;
  }}

  if (!deck.length) {{
    rebuildDeck();
  }}

  return deck.shift();
}}

async function fadeOutBoth() {{
  vid.classList.add('fadeout');
  img.classList.add('fadeout');
  await wait(1000);
}}

async function fadeIn(el) {{
  el.classList.remove('fadeout');
  await wait(1000);
}}

async function showVideo(src) {{
  clearImageTimer();
  img.style.display = 'none';
  vid.style.display = 'block';

  vid.src = src;

  await new Promise(resolve => {{
    const onCanPlay = () => {{
      vid.removeEventListener('canplay', onCanPlay);
      resolve();
    }};
    vid.addEventListener('canplay', onCanPlay);
  }});

  try {{ await vid.play(); }}
  catch(e){{
    await wait(300);
    try {{ await vid.play(); }} catch(_) {{}}
  }}

  await fadeIn(vid);
}}

async function showImage(src) {{
  clearImageTimer();

  try {{ vid.pause(); }} catch(_) {{}}
  vid.removeAttribute('src');
  vid.load();

  vid.style.display = 'none';
  img.style.display = 'block';

  await new Promise(resolve => {{
    img.onload = () => resolve();
    img.onerror = () => resolve();
    img.src = src;
  }});

  await fadeIn(img);

  imageTimer = setTimeout(async () => {{
    i = pickNextIndex();
    await playIndex(i);
  }}, PIC_SECONDS);
}}

async function playIndex(idx){{
  await refreshPlaylist();

  if(!items.length){{
    await wait(1000);
    return;
  }}

  const item = items[idx];
  await fadeOutBoth();

  const src = '/' + item.name;

  if (item.type === 'image') {{
    await showImage(src);
  }} else {{
    await showVideo(src);
  }}

  lastPlayed = idx;
  i = idx;
}}

vid.onended = async () => {{
  i = pickNextIndex();
  await playIndex(i);
}};

vid.onerror = async () => {{
  await refreshPlaylist();
  i = pickNextIndex();
  await playIndex(i);
}};

(async () => {{
  await refreshPlaylist();
  if(items.length){{
    if (RANDOM_START) {{
      if (!deck.length) rebuildDeck();
      i = deck.shift();
    }} else {{
      i = 0;
    }}
  }}
  await playIndex(i);
}})();

setInterval(refreshPlaylist, 10000);
</script>
</body>
</html>""")

            log("info", "Playlist HTML generated (videos+pics). PIC_SECONDS=%ss order=%s",
                CONFIG.get("PIC_SECONDS"), CONFIG.get("PLAY_ORDER"))
            return True

        except Exception as e:
            log("error", "Failed to generate playlist HTML: %s", e)
            return False

    def start(self):
        os.environ.setdefault("DISPLAY", ":0")

        # External mode: open external URL directly
 #       if external_mode_enabled():
 #           url = (CONFIG.get("EXTERNAL_URL") or "").strip()
 #           log("info", "External mode enabled — launching Edge to: %s", url)
 #
 #           if not os.path.isfile(self.edge_path):
 #               log("error", "Microsoft Edge binary not found at %s", self.edge_path)
 #               return False
 #
 #           cmd = [
 #               self.edge_path,
 #               "--kiosk",
 #               "--app=" + url,
 #               "--no-first-run",
 #               "--disable-infobars",
 #               "--autoplay-policy=no-user-gesture-required",
 #               "--new-window",
 #               f"--user-data-dir={self.profile_dir}",
 #           ]
 #
 #           try:
 #               self.proc = subprocess.Popen(
 #                   cmd,
 #                   start_new_session=True,
 #                   stdout=subprocess.DEVNULL,
 #                   stderr=subprocess.STDOUT,
 #               )
 #               log("info", "Edge started successfully (external mode) (PID %s)", self.proc.pid)
 #               return True
 #           except Exception as e:
 #               log("error", "Failed to launch Edge (external mode): %s", e)
 #               return False

        # If external is enabled but invalid URL, warn and fall back to local mode
 #       if CONFIG.get("EXTERNAL_WEBSERVER_ENABLED") and not external_mode_enabled():
 #           log("warning", "External mode enabled but externalurl is invalid: %r", CONFIG.get("EXTERNAL_URL"))

        # Local mode: start HTTP server + playlist HTML
        try:
            self.http_server = ThreadingHTTPServer(("127.0.0.1", 0), VideoHandler)
            self.http_server_thread = threading.Thread(
                target=self.http_server.serve_forever, daemon=True
            )
            self.http_server_thread.start()
            port = self.http_server.server_address[1]
            log("info", "HTTP server started on port %d (serving /tmp + videos + pics)", port)
        except Exception as e:
            log("error", "Cannot start HTTP server: %s", e)
            return False

        if not self.generate_playlist():
            self.stop_http_server()
            return False

        if not os.path.isfile(self.edge_path):
            log("error", "Microsoft Edge binary not found at %s", self.edge_path)
            self.stop_http_server()
            return False

        url = f"http://127.0.0.1:{port}/screensaver_playlist.html"
        cmd = [
            self.edge_path,
            "--kiosk",
            "--app=" + url,
            "--no-first-run",
            "--disable-infobars",
            "--autoplay-policy=no-user-gesture-required",
            "--new-window",
            "--disable-features=Translate",
            f"--user-data-dir={self.profile_dir}",
        ]

        try:
            self.proc = subprocess.Popen(
                cmd,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            log("info", "Edge started successfully (local mode) (PID %s)", self.proc.pid)
            return True
        except Exception as e:
            log("error", "Failed to launch Edge (local mode): %s", e)
            self.stop_http_server()
            return False

    def stop_http_server(self):
        if self.http_server:
            try:
                log("info", "Shutting down HTTP server...")
                self.http_server.shutdown()
                self.http_server.server_close()
                if self.http_server_thread and self.http_server_thread.is_alive():
                    self.http_server_thread.join(timeout=2)
            except Exception as e:
                log("warning", "HTTP server shutdown issue: %s", e)
            finally:
                self.http_server = None
                self.http_server_thread = None

    def _pkill_edge_profile(self, sig="-TERM"):
        try:
            subprocess.run(
                ["pkill", sig, "-f", self.profile_dir],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            log("warning", "pkill fallback failed: %s", e)

    def stop(self):
        if self.proc and self.proc.poll() is None:
            try:
                pgid = os.getpgid(self.proc.pid)
                os.killpg(pgid, signal.SIGTERM)
                time.sleep(0.7)
                if self.proc.poll() is None:
                    os.killpg(pgid, signal.SIGKILL)
                log("info", "Edge starter process group terminated.")
            except Exception as e:
                log("warning", "Failed to terminate Edge PGID cleanly: %s", e)

        self._pkill_edge_profile("-TERM")
        time.sleep(0.5)
        self._pkill_edge_profile("-KILL")

        self.proc = None
        self.stop_http_server()

    def is_running(self):
        if self.proc and self.proc.poll() is None:
            return True
        try:
            out = subprocess.check_output(["pgrep", "-f", self.profile_dir], text=True).strip()
            return bool(out)
        except subprocess.CalledProcessError:
            return False


# -------------------------------
# Main loop
# -------------------------------
def screensaver_loop():
    player = None
    try:
        while True:
            idle = system_idle_seconds()
            if CONFIG["ALWAYS_START"] or idle >= CONFIG["IDLE_SECONDS"]:
                media = []
                if not external_mode_enabled():
                    media = list_media_items()
                    if not media:
                        log("warning", "No media found (videos/pics). Screensaver will show message page.")

                player = EdgePlayer()
                if not player.start():
                    log("error", "Failed to start screensaver.")
                    time.sleep(5)
                    continue

                drain_events()
                ignore_until = time.time() + 3.0

                prev_idle = system_idle_seconds()
                pending_motion = None

                allow_idle_trigger = (not media) and (not external_mode_enabled())

                while player.is_running():
                    curr_idle = system_idle_seconds()
                    armed = time.time() >= ignore_until

                    did_interact, pending_motion = confirmed_interaction(
                        armed, prev_idle, curr_idle, pending_motion
                    )

                    if (not did_interact) and allow_idle_trigger and armed:
                        if idle_dropped(prev_idle, curr_idle, threshold=2.0):
                            did_interact = True

                    if did_interact:
                        log("info", "User interaction detected – stopping screensaver.")
                        if CONFIG["PIN_ENABLED"]:
                            disable_ctrl_esc()
                            correct = pin_dialog(CONFIG["PIN_CODE"])
                            enable_ctrl_esc()
                            if correct:
                                player.stop()
                                break
                            else:
                                log("info", "Incorrect PIN – screensaver continues.")
                                pending_motion = None
                                ignore_until = time.time() + 1.0
                        else:
                            player.stop()
                            break

                    prev_idle = curr_idle
                    time.sleep(0.5)

                if player.is_running():
                    log("warning", "Edge still running – forcing termination.")
                    player.stop()

                break
            else:
                time.sleep(1)
    finally:
        if player:
            player.stop()
        log("info", "Cleanup complete.")


# -------------------------------
# Entrypoint
# -------------------------------
def main():
    # Env overrides
    if "SCREENSAVER_PIN" in os.environ:
        CONFIG["PIN_CODE"] = os.environ["SCREENSAVER_PIN"]
    if "SCREENSAVER_IDLE" in os.environ:
        CONFIG["IDLE_SECONDS"] = int(os.environ["SCREENSAVER_IDLE"])
    if "SCREENSAVER_PIN_ENABLED" in os.environ:
        CONFIG["PIN_ENABLED"] = os.environ["SCREENSAVER_PIN_ENABLED"].lower() not in ("0", "false")
    if "SCREENSAVER_DEBUG" in os.environ:
        CONFIG["DEBUG"] = os.environ["SCREENSAVER_DEBUG"].lower() in ("1", "true")
    if "SCREENSAVER_LOG" in os.environ:
        CONFIG["LOGGING_ENABLED"] = os.environ["SCREENSAVER_LOG"].lower() not in ("0", "false")
    if "SCREENSAVER_ALWAYS_START" in os.environ:
        CONFIG["ALWAYS_START"] = os.environ["SCREENSAVER_ALWAYS_START"].lower() in ("1", "true")

    # External mode env overrides
#    if "SCREENSAVER_EXTERNAL" in os.environ:
#        CONFIG["EXTERNAL_WEBSERVER_ENABLED"] = os.environ["SCREENSAVER_EXTERNAL"].lower() in ("1", "true")
#    if "SCREENSAVER_EXTERNAL_URL" in os.environ:
#        CONFIG["EXTERNAL_URL"] = os.environ["SCREENSAVER_EXTERNAL_URL"]

    # Picture env overrides (optional)
    if "SCREENSAVER_PICS_DIR" in os.environ:
        CONFIG["PICS_DIR"] = os.environ["SCREENSAVER_PICS_DIR"]
    if "SCREENSAVER_PIC_SECONDS" in os.environ:
        CONFIG["PIC_SECONDS"] = int(os.environ["SCREENSAVER_PIC_SECONDS"])

    if LOGGER:
        LOGGER.setLevel(logging.DEBUG if CONFIG.get("DEBUG") else logging.INFO)

    log("info", "Video+Picture Screensaver started - Config: %s", CONFIG)

#    if CONFIG.get("EXTERNAL_WEBSERVER_ENABLED"):
#        if external_mode_enabled():
#            log("info", "External mode ACTIVE: %s", CONFIG.get("EXTERNAL_URL"))
#        else:
#            log("warning", "External mode configured but invalid URL: %r", CONFIG.get("EXTERNAL_URL"))

    try:
        screensaver_loop()
    except KeyboardInterrupt:
        log("info", "Exited via Ctrl+C")
    except Exception as e:
        log("error", "Fatal error: %s", e)
        sys.exit(1)
    finally:
        log("info", "Screensaver script terminated.")


if __name__ == "__main__":
    main()
