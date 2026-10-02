#!/usr/bin/env python3
"""
IGEL Virtual Smartcard Minimal Utility

Purpose
-------
- One lightweight virtual reader/card.
- Automatically scans /userhome/.config/igelvsc/*.pfx
- Automatically inserts the selected certificate.
- PIV is the default card personality; --cac switches to CAC.
- PFX passwords may be encrypted and stored unless --nopwdstore is used.
- Default virtual-card PIN is 000000.
- PIN can be changed/reset from the tray. For password-protected PFX files,
  the PFX password must be supplied and validated before the PIN is changed.
- The virtual card is removed when the utility exits.

This utility reuses the tested PIV/CAC/vpcd backend from
igel_virtual_smartcard.py but does not create the full manager window.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import shlex
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

# The full backend must live beside this script in the packaged app.
from igel_virtual_smartcard import (
    PivCard,
    CacCard,
    VpcdTransport,
    PACKAGED_VPCD_CONF,
    PACKAGED_VPCD_DRIVER,
    PACKAGED_VPCD_DRIVER_REAL,
    find_tray_icon,
)

APP_NAME = "IGEL Virtual Smartcard Minimal"
VERSION = "0.4"

# Intentionally fixed to the IGEL user home requested for this utility.
BASE = Path("/userhome/.config/igelvsc")
MINIMAL_DIR = BASE / "minimal"
CERTSTORE_DIR = BASE / "mini-utility-certstore"
RUNTIME_DIR = BASE / "runtime-minimal"
READER_DIR = RUNTIME_DIR / "reader.conf.d"
VPCD_CONF = READER_DIR / "vpcd"
LOG_DIR = BASE / "logs"
MASTER_KEY = BASE / "master.key"
VPCD_PORT = 35963


def ensure_dirs():
    for p in (BASE, MINIMAL_DIR, CERTSTORE_DIR, RUNTIME_DIR, READER_DIR, LOG_DIR):
        p.mkdir(parents=True, exist_ok=True)


def master_key():
    if MASTER_KEY.exists():
        data = MASTER_KEY.read_bytes()
        if len(data) != 32:
            raise RuntimeError(f"Invalid master key: {MASTER_KEY}")
        return data
    key = get_random_bytes(32)
    MASTER_KEY.write_bytes(key)
    os.chmod(MASTER_KEY, 0o600)
    return key


def encrypt_secret(value):
    nonce = get_random_bytes(12)
    cipher = AES.new(master_key(), AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(value.encode("utf-8"))
    return {
        "version": 1,
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
        "tag": base64.b64encode(tag).decode("ascii"),
    }


def decrypt_secret(blob):
    cipher = AES.new(
        master_key(),
        AES.MODE_GCM,
        nonce=base64.b64decode(blob["nonce"]),
    )
    return cipher.decrypt_and_verify(
        base64.b64decode(blob["ciphertext"]),
        base64.b64decode(blob["tag"]),
    ).decode("utf-8")


def save_secret(path, value):
    path.write_text(json.dumps(encrypt_secret(value), indent=2) + "\n", encoding="utf-8")
    os.chmod(path, 0o600)


def load_secret(path):
    return decrypt_secret(json.loads(path.read_text(encoding="utf-8")))


def pfx_id(path):
    return hashlib.sha256(str(path.resolve()).encode("utf-8")).hexdigest()[:20]


def run_bytes(args, timeout=15):
    return subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def _openssl_pkcs12(args):
    """
    Run an OpenSSL PKCS#12 operation. If OpenSSL 3 rejects an older PFX because
    it uses a legacy cipher/provider, retry with -legacy.
    """
    base = ["openssl", "pkcs12"]
    p = run_bytes(base + args)
    if p.returncode == 0:
        return p

    err = p.stderr.decode(errors="replace")
    legacy_markers = (
        "unsupported",
        "legacy",
        "RC2",
        "Algorithm",
        "digital envelope routines",
    )
    if any(x.lower() in err.lower() for x in legacy_markers):
        p2 = run_bytes(base + ["-legacy"] + args)
        return p2
    return p


def verify_pfx_password(path, password, return_detail=False):
    """
    Validate the PKCS#12 password without extracting the certificate.

    v0.1 used '-clcerts -nokeys -out /dev/null'. A perfectly valid password
    could therefore be reported as wrong when OpenSSL could verify the PFX MAC
    but could not decrypt an older certificate bag (for example legacy RC2).

    '-noout' verifies the PKCS#12/MAC without requiring certificate extraction.
    """
    p = _openssl_pkcs12([
        "-in", str(path),
        "-noout",
        "-passin", f"pass:{password}",
    ])
    ok = p.returncode == 0
    detail = p.stderr.decode(errors="replace").strip()
    return (ok, detail) if return_detail else ok


def pfx_is_unprotected(path):
    return verify_pfx_password(path, "")


def extract_cert(path, password, output):
    p = _openssl_pkcs12([
        "-in", str(path),
        "-nokeys", "-clcerts",
        "-passin", f"pass:{password}",
        "-out", str(output),
    ])
    if p.returncode != 0:
        raise RuntimeError(
            p.stderr.decode(errors="replace").strip()
            or "Could not extract certificate from the PFX"
        )
    os.chmod(output, 0o600)


def probe_virtual_readers():
    code = r"""
from smartcard.System import readers
for r in readers():
    print(r)
"""
    try:
        p = subprocess.run(
            [sys.executable, "-c", code],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=6,
            check=False,
        )
        return [x.strip() for x in p.stdout.splitlines() if "Virtual PCD" in x]
    except Exception:
        return []


def runtime_driver():
    if PACKAGED_VPCD_DRIVER.exists():
        return PACKAGED_VPCD_DRIVER
    if PACKAGED_VPCD_DRIVER_REAL.exists():
        return PACKAGED_VPCD_DRIVER_REAL
    return None


def prepare_pcsc_config():
    driver = runtime_driver()
    if driver is None:
        raise RuntimeError("Packaged vpcd driver was not found")
    if not PACKAGED_VPCD_CONF.exists():
        raise RuntimeError(f"Missing packaged vpcd config: {PACKAGED_VPCD_CONF}")

    READER_DIR.mkdir(parents=True, exist_ok=True)

    # Preserve static physical reader definitions.
    sysdir = Path("/etc/reader.conf.d")
    if sysdir.is_dir():
        for src in sysdir.iterdir():
            if not src.is_file() or src.name == "vpcd":
                continue
            try:
                dst = READER_DIR / ("system-" + src.name)
                dst.write_bytes(src.read_bytes())
                os.chmod(dst, 0o600)
            except Exception:
                pass

    lines = []
    replaced = False
    for line in PACKAGED_VPCD_CONF.read_text(
        encoding="utf-8", errors="replace"
    ).splitlines():
        if line.lstrip().startswith("LIBPATH"):
            lines.append(f"LIBPATH      {driver}")
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        lines.append(f"LIBPATH      {driver}")

    VPCD_CONF.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.chmod(VPCD_CONF, 0o600)


def ensure_virtual_reader(log):
    if probe_virtual_readers():
        return None

    prepare_pcsc_config()
    pcscd = shutil.which("pcscd") or "/sbin/pcscd"
    logfile = LOG_DIR / "minimal-pcscd.log"
    fh = open(logfile, "ab", buffering=0)
    command = (
        "systemctl stop pcscd.socket pcscd.service 2>/dev/null || true; "
        "pkill -x pcscd 2>/dev/null || true; "
        f"exec {pcscd} --foreground --config '{READER_DIR}'"
    )
    log("Starting PC/SC helper for Virtual PCD")
    proc = subprocess.Popen(
        ["su", "-c", command, "root"],
        stdout=fh,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    deadline = time.time() + 8
    while time.time() < deadline:
        time.sleep(0.35)
        if probe_virtual_readers():
            return proc
        if proc.poll() is not None:
            break
    raise RuntimeError(f"Virtual PCD did not appear; see {logfile}")


def repair_certstore_permissions(log):
    """
    Normalize the minimal utility certificate store for the IGEL login account.

    IGEL OS has the user account "user", but it does not necessarily have a
    matching group named "user". Therefore use owner-only chown syntax:

        chown user <path>

    rather than:

        chown user:user <path>

    Permissions are deliberately restrictive:
      directories: 0700
      files:       0600

    This is sufficient for the owning user to enumerate, read and replace PFX
    files without exposing private-key material to other local users.
    """
    CERTSTORE_DIR.mkdir(parents=True, exist_ok=True)

    q = shlex.quote(str(CERTSTORE_DIR))
    command = (
        f"chown -R user {q} && "
        f"chmod 700 {q} && "
        f"find {q} -type d -exec chmod 700 {{}} \\\\; && "
        f"find {q} -type f -exec chmod 600 {{}} \\\\;"
    )
    try:
        p = subprocess.run(
            ["su", "-c", command, "root"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=15,
            check=False,
        )
        if p.returncode != 0:
            log(
                "Certificate-store permission repair returned "
                f"{p.returncode}: {p.stdout.strip()}"
            )
        else:
            log(
                "Certificate-store ownership/access normalized "
                "(owner=user, directories=0700, files=0600)"
            )
        return p.returncode == 0
    except Exception as exc:
        log(f"Certificate-store permission repair failed: {exc}")
        return False


def certstore_signature():
    result = []
    try:
        for p in CERTSTORE_DIR.iterdir():
            if p.is_file():
                st = p.stat()
                result.append((p.name, st.st_mtime_ns, st.st_size, st.st_uid, st.st_gid))
    except Exception:
        pass
    return tuple(sorted(result))


class MinimalVSC:
    def __init__(self, args):
        ensure_dirs()
        self.args = args
        self.card_type = "cac" if args.cac else "piv"
        self.pcscd_helper = None
        self._certstore_signature = ()
        self.backend = None
        self.current_pfx = None
        self.current_password = None
        self.inserted = False

        self.tray = Gtk.StatusIcon()
        icon = find_tray_icon()
        if icon:
            self.tray.set_from_file(str(icon))
        else:
            self.tray.set_from_icon_name("application-x-pkcs12")
        self.tray.set_visible(True)
        self.tray.connect("popup-menu", self.on_menu)
        self.tray.connect("activate", self.on_activate)

        signal.signal(signal.SIGTERM, self.signal_quit)
        signal.signal(signal.SIGINT, self.signal_quit)

        self.pcscd_helper = ensure_virtual_reader(self.log)

        # Normalize ownership before OpenSSL tries to open any PFX.
        repair_certstore_permissions(self.log)
        self._certstore_signature = certstore_signature()
        GLib.timeout_add_seconds(2, self.watch_certstore)

        files = self.pfx_files()
        if not files:
            self.error(
                "No PFX file found.\n\n"
                "Place a certificate in:\n"
                "/userhome/.config/igelvsc/mini-utility-certstore/"
            )
            raise SystemExit(2)

        # Automatic selection/insertion: first file alphabetically.
        self.select_certificate(files[0])

    def log(self, msg):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)
        return False

    def watch_certstore(self):
        """
        Poll for runtime file additions/changes. When anything changes, rerun
        ownership/access normalization so files copied in by root immediately
        become usable by the normal IGEL user.
        """
        sig = certstore_signature()
        if sig != self._certstore_signature:
            self.log("Certificate store changed; normalizing ownership/access")
            repair_certstore_permissions(self.log)
            self._certstore_signature = certstore_signature()
        return True

    def pfx_files(self):
        return sorted(CERTSTORE_DIR.glob("*.pfx"), key=lambda p: p.name.lower())

    def profile_dir(self, pfx):
        p = MINIMAL_DIR / pfx_id(pfx)
        p.mkdir(parents=True, exist_ok=True)
        return p

    def password_file(self, pfx):
        return self.profile_dir(pfx) / "pkcs12-password.enc.json"

    def pin_file(self, pfx):
        return self.profile_dir(pfx) / "virtual-pin.enc.json"

    def ensure_default_pin(self, pfx):
        f = self.pin_file(pfx)
        if not f.exists():
            save_secret(f, "000000")
        return load_secret(f)

    def prompt_password(self, pfx, allow_store=True, title="Certificate password"):
        d = Gtk.Dialog(title=title)
        d.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK,
        )
        box = d.get_content_area()
        box.set_spacing(8)

        lab = Gtk.Label(label=f"Password for:\n{pfx.name}")
        lab.set_xalign(0)
        box.pack_start(lab, False, False, 4)

        entry = Gtk.Entry()
        entry.set_visibility(False)
        entry.set_invisible_char("•")
        box.pack_start(entry, False, False, 4)

        store = Gtk.CheckButton(label="Store certificate password encrypted")
        store.set_active(True)
        store.set_sensitive(allow_store and not self.args.nopwdstore)
        if self.args.nopwdstore:
            store.set_active(False)
            store.set_tooltip_text("--nopwdstore is active")
        box.pack_start(store, False, False, 4)

        d.show_all()
        resp = d.run()
        value = entry.get_text()
        do_store = store.get_active()
        d.destroy()

        if resp != Gtk.ResponseType.OK:
            return None, False
        return value, do_store

    def resolve_password(self, pfx):
        # Unprotected containers need no prompt.
        if pfx_is_unprotected(pfx):
            return ""

        secret = self.password_file(pfx)
        if not self.args.nopwdstore and secret.exists():
            try:
                password = load_secret(secret)
                if verify_pfx_password(pfx, password):
                    return password
            except Exception:
                pass

        while True:
            password, store = self.prompt_password(pfx, allow_store=True)
            if password is None:
                return None
            ok, detail = verify_pfx_password(pfx, password, return_detail=True)
            if not ok:
                low = (detail or "").lower()
                if "mac verify" in low or "mac verify error" in low or "invalid password" in low:
                    self.error("Incorrect certificate password.")
                else:
                    self.error(
                        "The PFX could not be validated by OpenSSL.\n\n"
                        + (detail or "Unknown PKCS#12 error")
                    )
                continue
            if store and not self.args.nopwdstore:
                save_secret(secret, password)
            return password

    def make_profile(self, pfx, password):
        pdir = self.profile_dir(pfx)
        cert = pdir / "certificate.pem"
        extract_cert(pfx, password, cert)

        # Stable local link lets the tested backend load the source PFX without
        # copying it away from the requested top-level location.
        link = pdir / "certificate.pfx"
        try:
            if link.exists() or link.is_symlink():
                link.unlink()
            link.symlink_to(pfx)
        except Exception:
            shutil.copy2(pfx, link)

        pin = self.ensure_default_pin(pfx)

        meta = {
            "id": "minimal-" + pfx_id(pfx),
            "name": pfx.stem,
            "mode": "software",
            "card_type": self.card_type,
            "created": "minimal utility",
            "piv_guid": uuid.uuid5(uuid.NAMESPACE_URL, str(pfx.resolve())).hex,
            "certificates": [{"filename": cert.name, "info": {}}],
            "pkcs12": link.name,
            "pin_configured": True,
            "pin_secret_file": self.pin_file(pfx).name,
        }

        # PivCard expects secret files relative to profile_dir. pin_file already
        # is there. For the PFX password either persist it there, or supply it
        # only through ask_secret for this process.
        secret = self.password_file(pfx)
        if (not self.args.nopwdstore) and secret.exists():
            meta["store_pkcs12_password"] = True
            meta["pkcs12_password_file"] = secret.name
        else:
            meta["store_pkcs12_password"] = False

        return pdir, meta, pin

    def remove_card(self):
        if self.backend:
            try:
                self.backend.stop()
                self.backend.join(timeout=2)
            except Exception:
                pass
            self.backend = None
        self.inserted = False
        self.update_tooltip()
        self.log("Virtual card removed")

    def insert_current(self):
        if not self.current_pfx:
            return
        if self.inserted:
            self.remove_card()

        password = self.current_password
        pdir, meta, _pin = self.make_profile(self.current_pfx, password)

        def ask_secret(_title, _prompt):
            return password

        CardClass = CacCard if self.card_type == "cac" else PivCard
        card = CardClass(pdir, meta, ask_secret=ask_secret)
        self.log(f"Private key: {card._private_key_status()}")

        self.backend = VpcdTransport(
            card,
            [VPCD_PORT],
            self.log,
        )
        self.backend.start()

        deadline = time.time() + 4
        while time.time() < deadline and self.backend.port is None and self.backend.is_alive():
            while Gtk.events_pending():
                Gtk.main_iteration_do(False)
            time.sleep(0.05)

        if self.backend.port != VPCD_PORT:
            err = self.backend.last_error or "Could not connect to Virtual PCD 00 00"
            self.backend = None
            raise RuntimeError(err)

        self.inserted = True
        self.update_tooltip()
        self.log(
            f"Inserted {self.current_pfx.name} as {self.card_type.upper()} "
            f"in Virtual PCD 00 00"
        )

    def select_certificate(self, pfx):
        self.remove_card()
        password = self.resolve_password(pfx)
        if password is None:
            return False
        self.current_pfx = pfx
        self.current_password = password
        self.insert_current()
        return True

    def authenticate_for_pin_change(self):
        pfx = self.current_pfx
        if not pfx:
            return False

        if pfx_is_unprotected(pfx):
            # There is no PFX password to challenge. Verification of the empty
            # password is still performed above.
            return True

        while True:
            password, _unused = self.prompt_password(
                pfx,
                allow_store=False,
                title="Authorize PIN change",
            )
            if password is None:
                return False
            ok, detail = verify_pfx_password(pfx, password, return_detail=True)
            if ok:
                return True
            low = (detail or "").lower()
            if "mac verify" in low or "invalid password" in low:
                self.error("Incorrect certificate password. PIN was not changed.")
            else:
                self.error(
                    "The certificate password could not be validated. PIN was not changed.\n\n"
                    + (detail or "Unknown PKCS#12 error")
                )

    def change_pin(self, *_):
        if not self.current_pfx:
            return
        if not self.authenticate_for_pin_change():
            return

        while True:
            d = Gtk.Dialog(title="Change / reset virtual smartcard PIN")
            d.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK, Gtk.ResponseType.OK,
            )
            box = d.get_content_area()
            box.set_spacing(8)
            info = Gtk.Label(label="PIN must be 6 to 8 numeric digits.")
            info.set_xalign(0)
            box.pack_start(info, False, False, 4)

            a = Gtk.Entry()
            a.set_visibility(False)
            a.set_placeholder_text("New PIN")
            b = Gtk.Entry()
            b.set_visibility(False)
            b.set_placeholder_text("Confirm PIN")
            box.pack_start(a, False, False, 2)
            box.pack_start(b, False, False, 2)

            d.show_all()
            resp = d.run()
            p1 = a.get_text()
            p2 = b.get_text()
            d.destroy()

            if resp != Gtk.ResponseType.OK:
                return
            if not re.fullmatch(r"[0-9]{6,8}", p1 or ""):
                self.error("PIN must contain 6 to 8 numeric digits.")
                continue
            if p1 != p2:
                self.error("PIN confirmation does not match.")
                continue

            save_secret(self.pin_file(self.current_pfx), p1)
            was_inserted = self.inserted
            if was_inserted:
                self.insert_current()
            self.info("Virtual smartcard PIN changed.")
            return

    def update_tooltip(self):
        cert = self.current_pfx.name if self.current_pfx else "No certificate"
        state = "INSERTED" if self.inserted else "REMOVED"
        self.tray.set_tooltip_text(
            f"{APP_NAME} — {cert} — {self.card_type.upper()} — {state}"
        )

    def on_activate(self, *_):
        self.info(
            f"{APP_NAME} {VERSION}\n\n"
            f"Certificate: {self.current_pfx.name if self.current_pfx else 'None'}\n"
            f"Type: {self.card_type.upper()}\n"
            f"State: {'INSERTED' if self.inserted else 'REMOVED'}\n"
            f"Reader: Virtual PCD 00 00"
        )

    def on_menu(self, icon, button, activate_time):
        menu = Gtk.Menu()

        title = Gtk.MenuItem(
            label=f"{self.card_type.upper()} — "
                  f"{'INSERTED' if self.inserted else 'REMOVED'}"
        )
        title.set_sensitive(False)
        menu.append(title)
        menu.append(Gtk.SeparatorMenuItem())

        cert_head = Gtk.MenuItem(label="Certificate")
        cert_menu = Gtk.Menu()
        group = None
        for pfx in self.pfx_files():
            item = Gtk.RadioMenuItem.new_with_label(group, pfx.name)
            if group is None:
                group = item.get_group()
            item.set_active(self.current_pfx == pfx)
            item.connect("toggled", self.on_cert_menu, pfx)
            cert_menu.append(item)
        cert_head.set_submenu(cert_menu)
        menu.append(cert_head)

        menu.append(Gtk.SeparatorMenuItem())

        if self.inserted:
            item = Gtk.MenuItem(label="Remove virtual card")
            item.connect("activate", lambda *_: self.remove_card())
        else:
            item = Gtk.MenuItem(label="Insert virtual card")
            item.connect("activate", lambda *_: self.insert_current())
        menu.append(item)

        pin = Gtk.MenuItem(label="Change / reset PIN")
        pin.connect("activate", self.change_pin)
        menu.append(pin)

        menu.append(Gtk.SeparatorMenuItem())
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.quit)
        menu.append(quit_item)

        menu.show_all()
        menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, activate_time)

    def on_cert_menu(self, item, pfx):
        if item.get_active() and pfx != self.current_pfx:
            try:
                self.select_certificate(pfx)
            except Exception as exc:
                self.error(str(exc))

    def signal_quit(self, *_):
        GLib.idle_add(self.quit)

    def quit(self, *_):
        self.remove_card()
        Gtk.main_quit()
        return False

    @staticmethod
    def info(message):
        d = Gtk.MessageDialog(
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message,
        )
        d.run()
        d.destroy()

    @staticmethod
    def error(message):
        d = Gtk.MessageDialog(
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message,
        )
        d.run()
        d.destroy()

    def run(self):
        self.update_tooltip()
        Gtk.main()


def parse_args():
    p = argparse.ArgumentParser(description=APP_NAME)
    p.add_argument(
        "--cac",
        action="store_true",
        help="Expose the PFX as a CAC compatibility card. Without this option, PIV is used.",
    )
    p.add_argument(
        "--nopwdstore",
        action="store_true",
        help="Do not read or store encrypted PFX passwords; prompt when required",
    )
    return p.parse_args()


def main():
    args = parse_args()
    app = MinimalVSC(args)
    app.run()


if __name__ == "__main__":
    main()
