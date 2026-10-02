#!/usr/bin/env python3
"""
IGEL Virtual Smartcard v0.4.10

Highlights
----------
- Correct app name: IGEL Virtual Smartcard
- Persistent data in ~/.config/igelvsc
- Verifies that Virtual PCD readers are exposed through pcscd
- Software card backend speaks the vpcd protocol directly
- Imported certificate/PFX profiles can be inserted as a minimal PIV smart card
- PIV Authentication certificate is exposed through normal PC/SC
- RSA private-key operations are supported for imported PFX / PEM keys
- Physical-card snapshot import remains available
- Physical-card proxy profiles continue to use vsmartcard relay mode
- Existing tray controls and X11 global hotkeys remain

Security note
-------------
The program does not try to extract non-exportable keys from physical cards.
Proxy mode is used when the physical card must retain private-key operations.
"""

import json
import os
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

APP_NAME = "IGEL Virtual Smartcard"

CARD_TYPE_REGISTRY = [
    {
        "id": "piv",
        "label": "PIV-II",
        "description": "NIST PIV-II smartcard interface.",
    },
    {
        "id": "cac",
        "label": "CAC",
        "description": "Common Access Card compatibility using the CAC ID/authentication applet.",
    },
]
VERSION = "0.4.10"

CONFIG_DIR = Path.home() / ".config" / "igelvsc"
CARDS_DIR = CONFIG_DIR / "cards"
LOG_DIR = CONFIG_DIR / "logs"
CONFIG_FILE = CONFIG_DIR / "config.json"
STATE_FILE = CONFIG_DIR / "state.json"
VICC_LOG = LOG_DIR / "vicc.log"
APP_DIR = Path(__file__).resolve().parent

RUNTIME_DIR = CONFIG_DIR / "runtime"
RUNTIME_READER_DIR = RUNTIME_DIR / "reader.conf.d"
RUNTIME_VPCD_CONF = RUNTIME_READER_DIR / "vpcd"
MASTER_KEY_FILE = CONFIG_DIR / "master.key"

PACKAGED_VPCD_CONF = Path("/services/igelvirtualsmartcard/etc/reader.conf.d/vpcd")
PACKAGED_VPCD_DRIVER = Path("/services/igelvirtualsmartcard/usr/lib/pcsc/drivers/serial/libifdvpcd.so")
PACKAGED_VPCD_DRIVER_REAL = Path("/services/igelvirtualsmartcard/usr/lib/pcsc/drivers/serial/libifdvpcd.so.0.8")

ICON_CANDIDATES = [
    APP_DIR / "igel_virtual_smartcard_icon.svg",
    APP_DIR / "igel_virtual_smaartcard_icon_v2.svg",  # compatibility with the earlier filename
]

VPCD_PORTS = (35963, 35964)
PIV_AID = bytes.fromhex("A000000308000010000100")
CAC_RID = bytes.fromhex("A000000079")
CAC_PKI_AID_PREFIX = bytes.fromhex("A00000007901")

DEFAULT_CONFIG = {
    "active_card": None,
    "autoinsert": False,
    "preferred_vpcd_port": 35963,
    "reader_profiles": {"0": None, "1": None},
    "selected_reader": 0,
    "hotkeys": {
        "toggle": "Ctrl+Shift+F9",
        "next_card": "Ctrl+Shift+F10",
        "previous_card": "Ctrl+Shift+F11",
        "show_manager": "Ctrl+Shift+F12",
    },
}

DEFAULT_STATE = {
    "inserted": False,
    "profile_id": None,
    "backend": None,
    "vpcd_port": None,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_layout():
    for p in (CONFIG_DIR, CARDS_DIR, LOG_DIR, RUNTIME_DIR, RUNTIME_READER_DIR):
        p.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        save_json(CONFIG_FILE, DEFAULT_CONFIG)
    if not STATE_FILE.exists():
        save_json(STATE_FILE, DEFAULT_STATE)


def load_json(path, fallback):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return dict(fallback)


def save_json(path, obj):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.chmod(tmp, 0o600)
    tmp.replace(path)


def run_cmd(args, timeout=20, input_text=None):
    try:
        p = subprocess.run(
            args,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        return p.returncode, p.stdout
    except Exception as exc:
        return 127, str(exc)


def slugify(value):
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return value or f"card-{uuid.uuid4().hex[:8]}"


def safe_copy(src, dst, mode=0o600):
    shutil.copy2(src, dst)
    os.chmod(dst, mode)


def get_master_key():
    """
    Return a per-user 256-bit key used to encrypt stored certificate passwords.
    The key is persisted with mode 0600 under ~/.config/igelvsc/master.key.
    """
    from Cryptodome.Random import get_random_bytes

    if MASTER_KEY_FILE.exists():
        data = MASTER_KEY_FILE.read_bytes()
        if len(data) != 32:
            raise RuntimeError("Invalid IGEL Virtual Smartcard master.key")
        return data

    key = get_random_bytes(32)
    MASTER_KEY_FILE.write_bytes(key)
    os.chmod(MASTER_KEY_FILE, 0o600)
    return key


def encrypt_secret(secret_text):
    """
    AES-GCM encrypt a UTF-8 string and return JSON-safe fields.
    """
    import base64
    from Cryptodome.Cipher import AES
    from Cryptodome.Random import get_random_bytes

    key = get_master_key()
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(secret_text.encode("utf-8"))
    return {
        "version": 1,
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
        "tag": base64.b64encode(tag).decode("ascii"),
    }


def decrypt_secret(blob):
    import base64
    from Cryptodome.Cipher import AES

    key = get_master_key()
    nonce = base64.b64decode(blob["nonce"])
    ciphertext = base64.b64decode(blob["ciphertext"])
    tag = base64.b64decode(blob["tag"])
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plain = cipher.decrypt_and_verify(ciphertext, tag)
    return plain.decode("utf-8")


def find_tray_icon():
    for p in ICON_CANDIDATES:
        if p.exists():
            return p
    return None


def cert_info(path):
    info = {"path": str(path)}
    if not shutil.which("openssl"):
        info["error"] = "openssl not found"
        return info

    variants = [
        ["openssl", "x509", "-in", str(path)],
        ["openssl", "x509", "-inform", "DER", "-in", str(path)],
    ]
    out = ""
    ok = False
    for prefix in variants:
        rc, out = run_cmd(
            prefix + [
                "-noout", "-subject", "-issuer", "-serial",
                "-fingerprint", "-sha256", "-startdate", "-enddate"
            ]
        )
        if rc == 0:
            ok = True
            break
    if not ok:
        info["error"] = out.strip()
        return info

    for line in out.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            info[k.strip().lower().replace(" ", "_")] = v.strip()

    for prefix in variants:
        rc, text = run_cmd(prefix + ["-noout", "-text"])
        if rc == 0:
            m = re.search(r"Public Key Algorithm:\s*(.+)", text)
            if m:
                info["public_key_algorithm"] = m.group(1).strip()
            m = re.search(r"Public-Key:\s*\((\d+) bit\)", text)
            if m:
                info["public_key_bits"] = int(m.group(1))
            break
    return info


def _parse_openssl_cert_time(value):
    """Parse OpenSSL x509 notBefore/notAfter values as UTC datetimes."""
    if not value:
        return None
    value = str(value).strip()
    for fmt in (
        "%b %d %H:%M:%S %Y %Z",
        "%b %d %H:%M:%S %Y GMT",
    ):
        try:
            dt = datetime.strptime(value, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def certificate_validity(info, now=None):
    """Return normalized X.509 validity information for a cert_info() dict."""
    now = now or datetime.now(timezone.utc)
    not_before = _parse_openssl_cert_time(info.get("notbefore"))
    not_after = _parse_openssl_cert_time(info.get("notafter"))

    if not_before is None or not_after is None:
        return {
            "status": "UNKNOWN",
            "not_before": not_before,
            "not_after": not_after,
            "summary": "Certificate validity dates could not be parsed",
        }

    if now < not_before:
        delta = not_before - now
        days = max(0, int(delta.total_seconds() // 86400))
        return {
            "status": "NOT YET VALID",
            "not_before": not_before,
            "not_after": not_after,
            "summary": f"Starts in {days} day{'s' if days != 1 else ''}",
        }

    if now > not_after:
        delta = now - not_after
        days = max(0, int(delta.total_seconds() // 86400))
        return {
            "status": "EXPIRED",
            "not_before": not_before,
            "not_after": not_after,
            "summary": f"Expired {days} day{'s' if days != 1 else ''} ago",
        }

    delta = not_after - now
    days = max(0, int(delta.total_seconds() // 86400))
    return {
        "status": "VALID",
        "not_before": not_before,
        "not_after": not_after,
        "summary": f"{days} day{'s' if days != 1 else ''} remaining",
    }


def _format_cert_time(dt, raw_value):
    if dt is not None:
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    return str(raw_value or "Unknown")


def certificate_to_der(path):
    rc, out = run_cmd(
        ["openssl", "x509", "-in", str(path), "-outform", "DER", "-out", "/dev/stdout"],
        timeout=10,
    )
    if rc == 0:
        return out.encode("latin1") if isinstance(out, str) else out

    # subprocess text mode cannot safely carry DER. Use bytes mode.
    for args in (
        ["openssl", "x509", "-in", str(path), "-outform", "DER"],
        ["openssl", "x509", "-inform", "DER", "-in", str(path), "-outform", "DER"],
    ):
        try:
            p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            if p.returncode == 0:
                return p.stdout
        except Exception:
            pass
    raise RuntimeError(f"Could not convert certificate to DER: {path}")


def der_from_cert(path):
    for args in (
        ["openssl", "x509", "-in", str(path), "-outform", "DER"],
        ["openssl", "x509", "-inform", "DER", "-in", str(path), "-outform", "DER"],
    ):
        try:
            p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            if p.returncode == 0:
                return p.stdout
        except Exception:
            pass
    raise RuntimeError(f"Could not decode certificate {path}")


def tlv_len(n):
    if n < 0x80:
        return bytes([n])
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(raw)]) + raw


def tlv(tag, value):
    if isinstance(tag, int):
        if tag <= 0xFF:
            tagb = bytes([tag])
        elif tag <= 0xFFFF:
            tagb = tag.to_bytes(2, "big")
        else:
            tagb = tag.to_bytes(3, "big")
    else:
        tagb = tag
    return tagb + tlv_len(len(value)) + value


def read_tlv_length(data, pos):
    if pos >= len(data):
        raise ValueError("Missing TLV length")
    first = data[pos]
    pos += 1
    if first < 0x80:
        return first, pos
    n = first & 0x7F
    if n == 0 or pos + n > len(data):
        raise ValueError("Invalid TLV length")
    val = int.from_bytes(data[pos:pos+n], "big")
    return val, pos + n


def parse_tlvs(data):
    """Small BER-TLV parser sufficient for PIV GENERAL AUTHENTICATE templates."""
    result = []
    pos = 0
    while pos < len(data):
        start = pos
        first = data[pos]
        pos += 1
        tag_bytes = bytes([first])
        if first & 0x1F == 0x1F:
            while pos < len(data):
                b = data[pos]
                pos += 1
                tag_bytes += bytes([b])
                if not (b & 0x80):
                    break
        length, pos = read_tlv_length(data, pos)
        if pos + length > len(data):
            raise ValueError("TLV exceeds input")
        value = data[pos:pos+length]
        pos += length
        result.append((tag_bytes, value, start, pos))
    return result


def parse_apdu(apdu):
    if len(apdu) < 4:
        raise ValueError("APDU too short")
    cla, ins, p1, p2 = apdu[:4]
    data = b""
    le = None

    if len(apdu) == 4:
        return cla, ins, p1, p2, data, le

    if len(apdu) == 5:
        le = apdu[4] or 256
        return cla, ins, p1, p2, data, le

    b1 = apdu[4]
    if b1 != 0:
        lc = b1
        if len(apdu) < 5 + lc:
            raise ValueError("Short APDU truncated")
        data = apdu[5:5+lc]
        rest = apdu[5+lc:]
        if rest:
            le = rest[0] or 256
        return cla, ins, p1, p2, data, le

    # Extended APDU
    if len(apdu) < 7:
        le = 65536
        return cla, ins, p1, p2, data, le
    x = int.from_bytes(apdu[5:7], "big")
    if len(apdu) == 7:
        le = x or 65536
        return cla, ins, p1, p2, data, le
    lc = x
    if len(apdu) < 7 + lc:
        raise ValueError("Extended APDU truncated")
    data = apdu[7:7+lc]
    rest = apdu[7+lc:]
    if len(rest) >= 2:
        le = int.from_bytes(rest[:2], "big") or 65536
    return cla, ins, p1, p2, data, le


# ---------------------------------------------------------------------------
# vpcd transport
# ---------------------------------------------------------------------------

class VpcdTransport(threading.Thread):
    """
    Implements the small vpcd <-> virtual ICC framing protocol.

    vpcd exposes the reader through pcscd. This process only emulates the card.
    The reader itself remains the Virtual PCD device supplied by vsmartcard-vpcd.
    """

    CTRL_OFF = 0
    CTRL_ON = 1
    CTRL_RESET = 2
    CTRL_ATR = 4

    def __init__(self, card, ports, logger, stopped_callback=None):
        super().__init__(daemon=True)
        self.card = card
        self.ports = list(ports)
        self.logger = logger
        self.stopped_callback = stopped_callback
        self.sock = None
        self.running = False
        self.port = None
        self.last_error = None

    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.sock.close()
            except Exception:
                pass

    def _send(self, payload):
        self.sock.sendall(struct.pack("!H", len(payload)) + payload)

    def _recv_exact(self, n):
        chunks = []
        remaining = n
        while remaining:
            chunk = self.sock.recv(remaining)
            if not chunk:
                raise ConnectionError("vpcd disconnected")
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    def _recv(self):
        hdr = self._recv_exact(2)
        size = struct.unpack("!H", hdr)[0]
        return self._recv_exact(size) if size else b""

    def _connect(self):
        errors = []
        for port in self.ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2.0)
                s.connect(("127.0.0.1", int(port)))
                s.settimeout(None)
                self.sock = s
                self.port = int(port)
                return
            except Exception as exc:
                errors.append(f"{port}: {exc}")
                try:
                    s.close()
                except Exception:
                    pass
        raise ConnectionError("Could not connect to a Virtual PCD slot: " + "; ".join(errors))

    def run(self):
        try:
            self._connect()
            self.running = True
            self.logger(f"Software card connected to vpcd port {self.port}")
            while self.running:
                msg = self._recv()
                if len(msg) == 1:
                    ctrl = msg[0]
                    if ctrl == self.CTRL_OFF:
                        self.card.power_down()
                    elif ctrl == self.CTRL_ON:
                        self.card.power_up()
                    elif ctrl == self.CTRL_RESET:
                        self.card.reset()
                    elif ctrl == self.CTRL_ATR:
                        self._send(self.card.get_atr())
                    else:
                        self.logger(f"Unknown vpcd control command: {ctrl}")
                else:
                    self.logger("APDU > " + msg.hex(" ").upper())
                    response = self.card.execute(msg)
                    self.logger("APDU < " + response.hex(" ").upper())
                    self._send(response)
        except Exception as exc:
            self.last_error = str(exc)
            if self.running or self.port is None:
                self.logger(f"Software-card backend stopped: {exc}")
        finally:
            self.running = False
            if self.sock:
                try:
                    self.sock.close()
                except Exception:
                    pass
            if self.stopped_callback:
                GLib.idle_add(self.stopped_callback)


# ---------------------------------------------------------------------------
# Minimal PIV card implementation
# ---------------------------------------------------------------------------

class PivCard:
    """
    Minimal PIV-compatible card.

    v0.3 target:
      - OpenSC/PCSC sees the card
      - PIV application can be selected
      - PIV Authentication certificate can be read
      - PIN verify works
      - RSA GENERAL AUTHENTICATE private-key operation works for imported keys

    It is intentionally not a claim of full NIST PIV compliance.
    """

    # Common PIV object tags
    OBJ_CHUID = bytes.fromhex("5FC102")
    OBJ_CERT_AUTH = bytes.fromhex("5FC105")
    OBJ_CCC = bytes.fromhex("5FC107")
    OBJ_DISCOVERY = bytes.fromhex("7E")

    def __init__(self, profile_dir, meta, ask_secret=None):
        self.profile_dir = Path(profile_dir)
        self.meta = meta
        self.ask_secret = ask_secret
        self.selected = False
        self.verified = False
        self.pending = b""
        self.chain_buffer = b""
        self.chain_ins = None
        self.chain_p1 = None
        self.chain_p2 = None
        self.pin = self._load_virtual_pin()
        self.max_pin_retries = 5
        self.pin_retries = self.max_pin_retries
        self.cert_der = self._load_certificate()
        self.private_key = None
        self.key_kind = None
        self._load_private_key()

    def _load_virtual_pin(self):
        """
        Load the encrypted per-profile virtual smartcard PIN.
        No default PIN exists from v0.3.4 onward.
        """
        secret_name = self.meta.get("pin_secret_file")
        if not self.meta.get("pin_configured") or not secret_name:
            raise RuntimeError("Virtual smartcard PIN is not configured for this profile")

        secret_path = self.profile_dir / secret_name
        if not secret_path.exists():
            raise RuntimeError(f"Virtual smartcard PIN secret is missing: {secret_path}")

        try:
            blob = json.loads(secret_path.read_text(encoding="utf-8"))
            pin = decrypt_secret(blob)
        except Exception as exc:
            raise RuntimeError(f"Could not decrypt virtual smartcard PIN: {exc}")

        if not re.fullmatch(r"[0-9]{6,8}", pin or ""):
            raise RuntimeError("Stored virtual smartcard PIN is invalid; configure a 6-8 digit PIN")
        return pin

    def get_atr(self):
        # Stable T=1 ATR with historical bytes "IGELVSC03".
        # vpcd exposes this through pcscd as the ATR of the inserted card.
        return bytes.fromhex("3B 89 80 01 49 47 45 4C 56 53 43 30 33")

    def power_up(self):
        self.selected = False
        self.verified = False
        self.pending = b""
        self.chain_buffer = b""
        self.chain_ins = None
        self.chain_p1 = None
        self.chain_p2 = None
        self.pin_retries = self.max_pin_retries

    def power_down(self):
        self.selected = False
        self.verified = False
        self.pending = b""

    def reset(self):
        self.power_up()

    def _load_certificate(self):
        certs = self.meta.get("certificates", [])
        if not certs:
            raise RuntimeError("Profile contains no certificate")
        filename = certs[0].get("filename")
        if not filename:
            raise RuntimeError("Certificate filename missing from profile")
        return der_from_cert(self.profile_dir / filename)

    def _load_private_key(self):
        # Direct PEM/KEY import
        key_name = self.meta.get("private_key_file") or self.meta.get("private_key")
        if key_name and not str(key_name).startswith("not copied"):
            p = self.profile_dir / str(key_name)
            if p.exists():
                data = p.read_bytes()
                self.private_key = self._import_rsa_key(data, None)
                if self.private_key:
                    self.key_kind = "RSA"
                    return

        # PFX/P12: keep the original container and ask for its password at insert time.
        p12_name = self.meta.get("pkcs12")
        if p12_name:
            password = None

            # Prefer stored password when enabled for this profile.
            secret_name = self.meta.get("pkcs12_password_file")
            if self.meta.get("store_pkcs12_password", False) and secret_name:
                secret_path = self.profile_dir / secret_name
                if secret_path.exists():
                    try:
                        password = decrypt_secret(
                            json.loads(secret_path.read_text(encoding="utf-8"))
                        )
                    except Exception as exc:
                        raise RuntimeError(f"Could not decrypt stored PKCS#12 password: {exc}")

            if password is None:
                password = self.ask_secret(
                    "PKCS#12 password",
                    f"Password for {p12_name}:"
                ) if self.ask_secret else None

            if password is None:
                return

            p12_path = self.profile_dir / p12_name
            try:
                p = subprocess.run(
                    [
                        "openssl", "pkcs12",
                        "-in", str(p12_path),
                        "-nocerts", "-nodes",
                        "-passin", f"pass:{password}",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=15,
                )
                if p.returncode == 0:
                    # openssl pkcs12 may prepend "Bag Attributes" before the PEM.
                    # Extract only the actual private-key PEM block before handing
                    # it to PyCryptodome.
                    pem = p.stdout
                    match = re.search(
                        br"-----BEGIN (?:RSA )?PRIVATE KEY-----.*?-----END (?:RSA )?PRIVATE KEY-----",
                        pem,
                        re.DOTALL,
                    )
                    key_blob = match.group(0) if match else pem
                    self.private_key = self._import_rsa_key(key_blob, None)
                    if self.private_key:
                        self.key_kind = "RSA"
                    else:
                        raise RuntimeError("PKCS#12 private key was extracted but could not be imported")
                else:
                    raise RuntimeError(p.stderr.decode(errors="replace").strip())
            except Exception as exc:
                raise RuntimeError(f"Could not load PKCS#12 private key: {exc}")

    @staticmethod
    def _import_rsa_key(data, passphrase):
        try:
            from Cryptodome.PublicKey import RSA
            key = RSA.import_key(data, passphrase=passphrase)
            return key if key.has_private() else None
        except Exception:
            return None

    def _cert_object(self):
        # PIV certificate object: tag 70 certificate, tag 71 cert-info=00
        # FE is the error detection code field; zero-length is adequate here.
        body = tlv(0x70, self.cert_der) + tlv(0x71, b"\x00") + tlv(0xFE, b"")
        return tlv(0x53, body)

    def _chuid_object(self):
        # Synthetic CHUID sufficient for discovery/testing; not a real identity credential.
        guid = uuid.UUID(self.meta.get("piv_guid", uuid.uuid4().hex)).bytes
        fascn = b"\xD4" + b"\x00" * 24
        exp = b"20351231"
        body = (
            tlv(0x30, fascn) +
            tlv(0x34, guid) +
            tlv(0x35, exp) +
            tlv(0x3E, b"\x00" * 16) +
            tlv(0xFE, b"")
        )
        return tlv(0x53, body)

    def _ccc_object(self):
        # Minimal synthetic Card Capability Container.
        card_id = uuid.UUID(self.meta.get("piv_guid", uuid.uuid4().hex)).bytes
        body = (
            tlv(0xF0, b"\xA0\x00\x00\x01\x16\xFF\x02") +
            tlv(0xF1, card_id) +
            tlv(0xF2, b"\x21") +
            tlv(0xF3, b"\x00") +
            tlv(0xFE, b"")
        )
        return tlv(0x53, body)

    def _discovery_object(self):
        # PIV AID + PIN usage policy: application PIN is primary.
        aid = tlv(0x4F, PIV_AID)
        pin_policy = tlv(0x5F2F, b"\x40\x00")
        return tlv(0x7E, aid + pin_policy)

    def _select_response(self):
        # Application property template including AID.
        return tlv(0x61, tlv(0x4F, PIV_AID) + tlv(0x79, b"\x4F\x0B" + PIV_AID))

    def _get_data_object(self, data):
        # Request format: 5C <len> <object tag>
        try:
            items = parse_tlvs(data)
            tag_value = None
            for tag, value, _, _ in items:
                if tag == b"\x5C":
                    tag_value = value
                    break
            if tag_value is None:
                return None
        except Exception:
            return None

        if tag_value == self.OBJ_CERT_AUTH:
            return self._cert_object()
        if tag_value == self.OBJ_CHUID:
            return self._chuid_object()
        if tag_value == self.OBJ_CCC:
            return self._ccc_object()
        if tag_value == self.OBJ_DISCOVERY:
            return self._discovery_object()
        return None

    def _chunk_response(self, data, le):
        # For large certs, return as much as caller requested and expose the rest via GET RESPONSE.
        if le is None:
            le = 256
        if len(data) <= le:
            self.pending = b""
            return data + b"\x90\x00"
        chunk = data[:le]
        self.pending = data[le:]
        remain = min(len(self.pending), 255)
        return chunk + bytes([0x61, remain if remain else 0x00])

    def _get_response(self, le):
        if not self.pending:
            return b"\x6A\x86"
        n = le or 256
        chunk = self.pending[:n]
        self.pending = self.pending[n:]
        if self.pending:
            remain = min(len(self.pending), 255)
            return chunk + bytes([0x61, remain if remain else 0x00])
        return chunk + b"\x90\x00"

    def _verify(self, p1, p2, data):
        """
        PIV VERIFY behavior for the application PIN (key reference 0x80).

        - P1=0x00 with no data: status query, return 63Cx and do not decrement.
        - P1=0x00 with 8-byte PIN block: verify 6-8 ASCII digits padded with FF.
        - P1=0xFF with no data: logout/reset authenticated state.
        """
        if p2 not in (0x80, 0x00):
            return b"\x6A\x88"

        # Logout / reset PIN security status.
        if p1 == 0xFF:
            if data:
                return b"\x6A\x86"
            self.verified = False
            return b"\x90\x00"

        if p1 != 0x00:
            return b"\x6A\x86"

        # Query current verification/retry state. This must never consume a retry.
        if len(data) == 0:
            if self.verified:
                return b"\x90\x00"
            if self.pin_retries <= 0:
                return b"\x69\x83"
            return bytes([0x63, 0xC0 | min(self.pin_retries, 0x0F)])

        # PIV PIN VERIFY uses an 8-byte PIN block padded with FF.
        if len(data) != 8:
            return b"\x67\x00"

        pin_bytes = data.rstrip(b"\xFF")
        if not (6 <= len(pin_bytes) <= 8):
            return b"\x63\xC0" if self.pin_retries <= 0 else bytes(
                [0x63, 0xC0 | min(self.pin_retries, 0x0F)]
            )

        try:
            candidate = pin_bytes.decode("ascii")
        except UnicodeDecodeError:
            candidate = ""

        valid_format = re.fullmatch(r"[0-9]{6,8}", candidate or "") is not None

        if valid_format and candidate == self.pin:
            self.verified = True
            self.pin_retries = self.max_pin_retries
            return b"\x90\x00"

        self.verified = False
        self.pin_retries = max(0, self.pin_retries - 1)

        if self.pin_retries == 0:
            return b"\x69\x83"

        return bytes([0x63, 0xC0 | min(self.pin_retries, 0x0F)])

    def _private_key_status(self):
        if not self.private_key:
            return "missing"
        try:
            bits = int(self.private_key.size_in_bits())
        except Exception:
            return "invalid"
        return f"RSA-{bits}"

    def _general_authenticate(self, algorithm, key_ref, data):
        if key_ref != 0x9A:
            return b"\x6A\x88"
        if not self.verified:
            return b"\x69\x82"
        if not self.private_key:
            return b"\x69\x85"
        if self.key_kind != "RSA":
            return b"\x6A\x81"

        # PIV RSA algorithm identifiers: 0x06 RSA-1024, 0x07 RSA-2048.
        if algorithm not in (0x06, 0x07):
            return b"\x6A\x80"

        try:
            outer = parse_tlvs(data)
            if not outer or outer[0][0] != b"\x7C":
                return b"\x6A\x80"
            inner = parse_tlvs(outer[0][1])
            challenge = None
            for tag, value, _, _ in inner:
                if tag == b"\x81":
                    challenge = value
            if challenge is None:
                return b"\x6A\x80"

            k = (self.private_key.size_in_bits() + 7) // 8
            if len(challenge) > k:
                return b"\x67\x00"
            challenge = challenge.rjust(k, b"\x00")

            # PIV RSA GENERAL AUTHENTICATE performs the raw RSA private operation;
            # host middleware supplies the encoded input block.
            m = int.from_bytes(challenge, "big")
            s = pow(m, int(self.private_key.d), int(self.private_key.n))
            sig = s.to_bytes(k, "big")
            return tlv(0x7C, tlv(0x82, sig)) + b"\x90\x00"
        except Exception:
            return b"\x6F\x00"

    def execute(self, apdu):
        try:
            cla, ins, p1, p2, data, le = parse_apdu(apdu)
        except Exception:
            return b"\x67\x00"

        # ISO 7816 command chaining.
        #
        # OpenSC sends RSA-2048 PIV GENERAL AUTHENTICATE as at least two APDUs.
        # The first APDU uses CLA bit 0x10 ("more blocks") and carries 255 bytes.
        # Earlier versions incorrectly tried to execute that incomplete 7C
        # template immediately.
        more_blocks = bool(cla & 0x10)
        base_cla = cla & ~0x10

        if more_blocks:
            if self.chain_ins is None:
                self.chain_ins = ins
                self.chain_p1 = p1
                self.chain_p2 = p2
                self.chain_buffer = bytes(data)
            else:
                if (ins, p1, p2) != (self.chain_ins, self.chain_p1, self.chain_p2):
                    self.chain_buffer = b""
                    self.chain_ins = self.chain_p1 = self.chain_p2 = None
                    return b"\x68\x83"
                self.chain_buffer += bytes(data)

            # Intermediate chained command completed successfully.
            return b"\x90\x00"

        # Final command in a chain: append it to the accumulated data.
        if self.chain_ins is not None:
            if (ins, p1, p2) != (self.chain_ins, self.chain_p1, self.chain_p2):
                self.chain_buffer = b""
                self.chain_ins = self.chain_p1 = self.chain_p2 = None
                return b"\x68\x83"

            data = self.chain_buffer + bytes(data)
            self.chain_buffer = b""
            self.chain_ins = self.chain_p1 = self.chain_p2 = None

        # SELECT application
        if ins == 0xA4 and p1 == 0x04:
            if data in (PIV_AID, PIV_AID[:-2]):
                self.selected = True
                return self._chunk_response(self._select_response(), le or 256)
            return b"\x6A\x82"

        # GET RESPONSE
        if ins == 0xC0:
            return self._get_response(le)

        if not self.selected:
            return b"\x69\x99"

        # GET DATA
        if ins == 0xCB and p1 == 0x3F and p2 == 0xFF:
            obj = self._get_data_object(data)
            if obj is None:
                return b"\x6A\x88"
            return self._chunk_response(obj, le or 256)

        # VERIFY
        if ins == 0x20:
            return self._verify(p1, p2, data)

        # GENERAL AUTHENTICATE
        if ins == 0x87:
            return self._general_authenticate(p1, p2, data)

        return b"\x6D\x00"


# ---------------------------------------------------------------------------
# CAC compatibility card implementation
# ---------------------------------------------------------------------------

class CacCard(PivCard):
    """
    Minimal CAC compatibility card for OpenSC's CAC middleware path.

    v0.4.0 target:
      - expose a CAC PKI Identity applet at A0000000790100
      - expose the imported X.509 certificate through CAC READ FILE
      - support ISO VERIFY for the profile PIN
      - support CAC SIGN/DECRYPT (INS 0x42) with 240-byte stepping
      - perform the same raw RSA private operation used by CAC middleware

    This first CAC implementation focuses on the CAC ID / authentication slot.
    It does not yet emulate the full CCC/ACA/general-container data model or
    separate email-signature/encryption key pairs.
    """

    CAC_INS_GET_CERTIFICATE = 0x36   # legacy compatibility probe
    CAC_INS_SIGN_DECRYPT = 0x42
    CAC_INS_READ_FILE = 0x52
    CAC_INS_GET_PROPERTIES = 0x56
    CAC_P1_STEP = 0x80
    CAC_P1_FINAL = 0x00
    CAC_FILE_TAG = 0x01
    CAC_FILE_VALUE = 0x02

    def __init__(self, profile_dir, meta, ask_secret=None):
        super().__init__(profile_dir, meta, ask_secret=ask_secret)
        self.cac_selected_slot = None
        self.cac_cert_offset = 0
        self.cac_crypto_buffer = b""

    def get_atr(self):
        # T=1 ATR with stable IGEL CAC historical bytes. OpenSC's CAC driver
        # identifies CAC primarily by probing its applications rather than by
        # requiring this exact ATR.
        return bytes.fromhex("3B 89 80 01 49 47 45 4C 43 41 43 34 30")

    def power_up(self):
        super().power_up()
        self.cac_selected_slot = None
        self.cac_cert_offset = 0
        self.cac_crypto_buffer = b""

    def power_down(self):
        super().power_down()
        self.cac_selected_slot = None
        self.cac_cert_offset = 0
        self.cac_crypto_buffer = b""

    @staticmethod
    def _cac_aid_for_slot(slot):
        return CAC_PKI_AID_PREFIX + bytes([slot & 0xFF])

    def _available_cac_slots(self):
        # v0.4.0 deliberately exposes the CAC ID slot only. The profile may
        # contain additional certs, but advertising them as CAC signing/
        # encryption slots without matching private keys would be misleading.
        return {0: self.cert_der}

    def _cac_select_aid(self, aid):
        for slot in self._available_cac_slots():
            if aid == self._cac_aid_for_slot(slot):
                self.cac_selected_slot = slot
                self.cac_cert_offset = 0
                self.cac_crypto_buffer = b""
                self.selected = True
                return b"\x90\x00"
        return b"\x6A\x82"

    def _cac_value_file(self):
        # CAC certificate value file: CERTINFO byte followed by DER certificate.
        # cert-info 0 means uncompressed certificate.
        return b"\x00" + self.cert_der

    def _cac_tl_file(self):
        # SimpleTLV tag/length descriptors for:
        #   71 length=1   (certificate information byte)
        #   70 length=N   (certificate)
        # OpenSC's CAC code expects 0xFF followed by a little-endian 16-bit
        # length for values larger than a short SimpleTLV length.
        cert_len = len(self.cert_der)
        if cert_len <= 0xFE:
            cert_tl = bytes([0x70, cert_len])
        else:
            cert_tl = bytes([0x70, 0xFF, cert_len & 0xFF, (cert_len >> 8) & 0xFF])
        return bytes([0x71, 0x01]) + cert_tl

    def _cac_read_file(self, p1, p2, data):
        if self.cac_selected_slot is None:
            return b"\x69\x99"
        if len(data) < 2:
            return b"\x67\x00"

        file_type = data[0]
        requested = data[1]
        blob = self._cac_tl_file() if file_type == self.CAC_FILE_TAG else (
            self._cac_value_file() if file_type == self.CAC_FILE_VALUE else None
        )
        if blob is None:
            return b"\x6A\x86"

        offset = (p1 << 8) | p2
        if offset == 0 and requested == 2:
            # CAC READ FILE starts by asking for the file size. The size is
            # returned little-endian and subsequent reads start at offset 2.
            size = len(blob)
            return bytes([size & 0xFF, (size >> 8) & 0xFF]) + b"\x90\x00"

        if offset < 2:
            return b"\x6B\x00"
        pos = offset - 2
        if pos > len(blob):
            return b"\x6B\x00"

        count = requested if requested else 256
        return blob[pos:pos + count] + b"\x90\x00"

    def _cac_get_certificate(self, le):
        # Legacy CAC1-compatible streaming interface. Supporting this probe as
        # well as CAC READ FILE makes the virtual card usable with older OpenSC
        # configurations without changing the primary modern CAC path.
        if self.cac_selected_slot is None:
            return b"\x69\x99"

        blob = self._cac_value_file()
        n = le or 256
        chunk = blob[self.cac_cert_offset:self.cac_cert_offset + n]
        self.cac_cert_offset += len(chunk)
        remain = len(blob) - self.cac_cert_offset
        if remain > 0:
            return chunk + bytes([0x63, min(remain, 0xFF)])
        return chunk + b"\x90\x00"

    def _cac_sign_decrypt(self, p1, data):
        if self.cac_selected_slot is None:
            return b"\x69\x99"
        if not self.verified:
            return b"\x69\x82"
        if not self.private_key or self.key_kind != "RSA":
            return b"\x69\x85"

        if p1 == self.CAC_P1_STEP:
            self.cac_crypto_buffer += bytes(data)
            return b"\x90\x00"

        if p1 != self.CAC_P1_FINAL:
            self.cac_crypto_buffer = b""
            return b"\x6A\x86"

        block = self.cac_crypto_buffer + bytes(data)
        self.cac_crypto_buffer = b""

        try:
            k = (self.private_key.size_in_bits() + 7) // 8
            if len(block) > k:
                return b"\x67\x00"
            block = block.rjust(k, b"\x00")
            m = int.from_bytes(block, "big")
            s = pow(m, int(self.private_key.d), int(self.private_key.n))
            result = s.to_bytes(k, "big")
            return result + b"\x90\x00"
        except Exception:
            return b"\x6F\x00"

    def execute(self, apdu):
        try:
            cla, ins, p1, p2, data, le = parse_apdu(apdu)
        except Exception:
            return b"\x67\x00"

        # CAC PKI applet selection. Slot 0 is CAC ID.
        if ins == 0xA4 and p1 == 0x04:
            return self._cac_select_aid(bytes(data))

        # Nothing except SELECT is valid before a CAC PKI applet is selected.
        if self.cac_selected_slot is None:
            return b"\x69\x99"

        if ins == self.CAC_INS_READ_FILE:
            return self._cac_read_file(p1, p2, data)

        if ins == self.CAC_INS_GET_CERTIFICATE:
            return self._cac_get_certificate(le)

        if ins == 0x20:  # ISO VERIFY
            return self._verify(p1, p2, data)

        if ins == self.CAC_INS_SIGN_DECRYPT:
            return self._cac_sign_decrypt(p1, data)

        if ins == 0x84:  # GET CHALLENGE
            return os.urandom(8) + b"\x90\x00"

        if ins == self.CAC_INS_GET_PROPERTIES:
            # Full CAC properties/ACA/CCC emulation is intentionally deferred.
            # Bare-CAC discovery in OpenSC does not require this command.
            return b"\x6D\x00"

        return b"\x6D\x00"


# ---------------------------------------------------------------------------
# Global X11 hotkeys
# ---------------------------------------------------------------------------

class HotkeyThread(threading.Thread):
    def __init__(self, app):
        super().__init__(daemon=True)
        self.app = app
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        try:
            from Xlib import X, XK, display
            d = display.Display()
            root = d.screen().root
            mods = X.ControlMask | X.ShiftMask
            lock_masks = (0, X.LockMask, X.Mod2Mask, X.LockMask | X.Mod2Mask)
            mapping = {
                XK.string_to_keysym("F9"): lambda: self.app.toggle_card(slot=0),
                XK.string_to_keysym("F10"): lambda: self.app.toggle_card(slot=1),
                XK.string_to_keysym("F11"): self.app.next_card,
                XK.string_to_keysym("F12"): self.app.show_manager,
            }
            actions = {}
            for keysym, action in mapping.items():
                kc = d.keysym_to_keycode(keysym)
                if not kc:
                    continue
                actions[kc] = action
                for extra in lock_masks:
                    root.grab_key(kc, mods | extra, True, X.GrabModeAsync, X.GrabModeAsync)
            d.sync()
            GLib.idle_add(self.app.log, "Global hotkeys active: Ctrl+Shift+F9 Reader 1 toggle, Ctrl+Shift+F10 Reader 2 toggle, Ctrl+Shift+F11 next profile, Ctrl+Shift+F12 manager")
            while self.running:
                if d.pending_events():
                    ev = d.next_event()
                    if ev.type == X.KeyPress and ev.detail in actions:
                        GLib.idle_add(actions[ev.detail])
                else:
                    time.sleep(0.05)
        except Exception as exc:
            GLib.idle_add(self.app.log, f"Global hotkeys unavailable: {exc}")


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class IgelVSC:
    def __init__(self):
        ensure_layout()
        self.config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
        self.state = load_json(STATE_FILE, DEFAULT_STATE)
        self._startup_restore_done = False
        self._quitting = False

        # v0.4.2: migrate the previous single active-card model into two
        # independently assignable Virtual PCD slots.
        if not isinstance(self.config.get("reader_profiles"), dict):
            self.config["reader_profiles"] = {"0": None, "1": None}
        self.config["reader_profiles"].setdefault("0", self.config.get("active_card"))
        self.config["reader_profiles"].setdefault("1", None)
        if self.config["reader_profiles"].get("0") is None and self.config.get("active_card"):
            self.config["reader_profiles"]["0"] = self.config.get("active_card")
        self.config.setdefault("selected_reader", 0)
        save_json(CONFIG_FILE, self.config)

        self.vicc_process = None  # legacy alias; proxy remains reader-0 only for now
        self.pcscd_process = None
        self.software_backend = None  # legacy alias to reader 0
        self.software_backends = {0: None, 1: None}
        self.physical_readers = []
        self.vpcd_readers = []

        self.window = Gtk.Window(title=f"{APP_NAME} {VERSION}")
        self.window.set_default_size(860, 620)
        self.window.connect("delete-event", self.on_window_delete)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        root.set_border_width(10)
        self.window.add(root)

        head = Gtk.Box(spacing=8)
        root.pack_start(head, False, False, 0)

        title = Gtk.Label()
        title.set_markup(f"<b>{APP_NAME}</b>  v{VERSION}")
        title.set_xalign(0)
        head.pack_start(title, True, True, 0)

        self.pcsc_label = Gtk.Label()
        self.pcsc_label.set_xalign(1)
        head.pack_end(self.pcsc_label, False, False, 0)

        self.status_label = Gtk.Label()
        self.status_label.set_xalign(0)
        root.pack_start(self.status_label, False, False, 0)

        self.notebook = Gtk.Notebook()
        root.pack_start(self.notebook, True, True, 0)

        self.build_cards_tab()
        self.build_physical_tab()
        self.build_diagnostics_tab()

        self.tray = Gtk.StatusIcon()
        icon = find_tray_icon()
        if icon:
            self.tray.set_from_file(str(icon))
        else:
            self.tray.set_from_icon_name("application-x-pkcs12")
        self.tray.set_visible(True)
        self.tray.set_tooltip_text(APP_NAME)
        self.tray.connect("popup-menu", self.on_tray_menu)
        self.tray.connect("activate", lambda *_: self.show_manager())

        self.refresh_profiles()

        # Do not import pyscard before a possible pcscd replacement.
        # A stale SCard context was the cause of the v0.3.1 IGEL failure.
        names, _detail = self._fresh_virtual_reader_names()
        if names:
            self.refresh_readers()
        else:
            self.vpcd_readers = []
            self.physical_readers = []
            self._rebuild_reader_detail_tabs()

        self.update_ui()

        self.hotkeys = HotkeyThread(self)
        self.hotkeys.start()
        GLib.timeout_add_seconds(2, self.health_check)

        self.log(f"{APP_NAME} v{VERSION}")
        self.log(f"Persistent data: {CONFIG_DIR}")
        self.log_pcsc_state()

        # Initialize the packaged vpcd reader if necessary. On IGEL OS the
        # privilege boundary is handled by `su -c ... root`; the GUI itself
        # remains in the normal user session.
        if not self.vpcd_readers:
            GLib.idle_add(self.ensure_virtual_readers, False)

        # Restore cards that were inserted when the application last quit.
        # Delay slightly so pcscd/Virtual PCD have time to become available.
        GLib.timeout_add_seconds(1, self._restore_previous_insertions)

    def _restore_previous_insertions(self):
        if self._startup_restore_done:
            return False

        wanted = self.state.get("readers", {}) if isinstance(self.state, dict) else {}
        requested = [
            slot for slot in (0, 1)
            if bool(wanted.get(str(slot), {}).get("inserted"))
        ]

        if not requested:
            self._startup_restore_done = True
            return False

        names, _detail = self._fresh_virtual_reader_names()
        if not names:
            # Keep waiting for the asynchronous PC/SC bootstrap.
            return True

        self._startup_restore_done = True
        for slot in requested:
            saved = wanted.get(str(slot), {})
            saved_pid = saved.get("profile_id")
            assigned = self.config.setdefault(
                "reader_profiles", {"0": None, "1": None}
            ).get(str(slot))

            # If the previous session recorded a concrete profile, restore the
            # same assignment before inserting.
            if saved_pid and saved_pid != assigned and self.profile_by_id(saved_pid)[1]:
                self.config["reader_profiles"][str(slot)] = saved_pid

            GLib.idle_add(self.insert_card, slot=slot)

        save_json(CONFIG_FILE, self.config)
        self.refresh_profiles()
        self.log(
            "Restoring previously inserted virtual reader(s): "
            + ", ".join(str(s + 1) for s in requested)
        )
        return False

    # ------------------------------------------------------------------ UI

    def build_cards_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_border_width(8)

        # Profile library controls remain global: import/delete operate on the
        # profile library, while reader-specific editing lives beside each reader.
        library_frame = Gtk.Frame(label="Certificate profiles")
        box.pack_start(library_frame, False, False, 0)
        library_row = Gtk.Box(spacing=6)
        library_row.set_border_width(6)
        library_frame.add(library_row)

        self.profile_combo = Gtk.ComboBoxText()
        self.profile_combo.connect("changed", self.on_profile_changed)
        library_row.pack_start(self.profile_combo, True, True, 0)

        b = Gtk.Button(label="Import certificate / PFX")
        b.connect("clicked", self.import_files)
        library_row.pack_start(b, False, False, 0)

        b = Gtk.Button(label="Delete profile")
        b.connect("clicked", self.delete_profile)
        library_row.pack_start(b, False, False, 0)

        # Two independent reader groups. The edit actions are deliberately
        # located below the profile assigned to that reader so their scope is
        # unambiguous.
        readers_frame = Gtk.Frame(label="Virtual readers")
        box.pack_start(readers_frame, False, False, 0)
        readers_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        readers_box.set_border_width(8)
        readers_frame.add(readers_box)

        self.reader_profile_combos = {}
        self.reader_state_labels = {}
        self.reader_action_buttons = {}
        self._refreshing_reader_combos = False

        for slot in (0, 1):
            rf = Gtk.Frame(label=f"Reader {slot + 1}  —  Virtual PCD 00 0{slot}")
            readers_box.pack_start(rf, False, False, 0)

            rb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            rb.set_border_width(7)
            rf.add(rb)

            top = Gtk.Box(spacing=6)
            rb.pack_start(top, False, False, 0)

            combo = Gtk.ComboBoxText()
            combo.connect("changed", self.on_reader_profile_changed, slot)
            self.reader_profile_combos[slot] = combo
            top.pack_start(combo, True, True, 0)

            state_label = Gtk.Label()
            state_label.set_size_request(105, -1)
            state_label.set_xalign(0.5)
            self.reader_state_labels[slot] = state_label
            top.pack_start(state_label, False, False, 0)

            insert_btn = Gtk.Button(label="Insert")
            insert_btn.connect("clicked", lambda _b, s=slot: self.insert_card(slot=s))
            top.pack_start(insert_btn, False, False, 0)

            remove_btn = Gtk.Button(label="Remove")
            remove_btn.connect("clicked", lambda _b, s=slot: self.remove_card(slot=s))
            top.pack_start(remove_btn, False, False, 0)

            actions = Gtk.Box(spacing=6)
            rb.pack_start(actions, False, False, 0)

            spacer = Gtk.Label(label="")
            spacer.set_size_request(18, -1)
            actions.pack_start(spacer, False, False, 0)

            pin_btn = Gtk.Button(label="Set / change PIN")
            pin_btn.connect("clicked", lambda _b, s=slot: self.reader_set_pin(s))
            actions.pack_start(pin_btn, False, False, 0)

            type_btn = Gtk.Button(label="Card type")
            type_btn.connect("clicked", lambda _b, s=slot: self.reader_set_card_type(s))
            actions.pack_start(type_btn, False, False, 0)

            pwd_btn = Gtk.Button(label="Certificate password")
            pwd_btn.connect("clicked", lambda _b, s=slot: self.reader_certificate_password(s))
            actions.pack_start(pwd_btn, False, False, 0)

            self.reader_action_buttons[slot] = {
                "insert": insert_btn,
                "remove": remove_btn,
                "pin": pin_btn,
                "card_type": type_btn,
                "password": pwd_btn,
            }

        # Reader-scoped profile information.
        details_frame = Gtk.Frame(label="Reader profile details")
        box.pack_start(details_frame, True, True, 0)

        self.reader_details_notebook = Gtk.Notebook()
        details_frame.add(self.reader_details_notebook)
        self.reader_profile_details = {}
        self.physical_reader_detail_views = {}
        self._physical_reader_tabs_signature = None

        for slot in (0, 1):
            tv = Gtk.TextView()
            tv.set_editable(False)
            tv.set_cursor_visible(False)
            tv.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            tv.set_left_margin(8)
            tv.set_right_margin(8)
            tv.set_top_margin(8)
            tv.set_bottom_margin(8)
            try:
                from gi.repository import Pango
                tv.modify_font(Pango.FontDescription("Monospace 10"))
            except Exception:
                pass

            sc = Gtk.ScrolledWindow()
            sc.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            sc.add(tv)

            self.reader_profile_details[slot] = tv
            self.reader_details_notebook.append_page(
                sc, Gtk.Label(label=f"Reader {slot + 1} profile")
            )

        self.notebook.append_page(box, Gtk.Label(label="Virtual Cards"))

    def build_physical_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_border_width(8)

        top = Gtk.Box(spacing=6)
        box.pack_start(top, False, False, 0)

        self.reader_combo = Gtk.ComboBoxText()
        top.pack_start(self.reader_combo, True, True, 0)

        b = Gtk.Button(label="Refresh")
        b.connect("clicked", lambda *_: self.refresh_readers())
        top.pack_start(b, False, False, 0)

        actions = Gtk.Box(spacing=6)
        box.pack_start(actions, False, False, 0)

        for label, cb in (
            ("Inspect physical card", self.inspect_physical_card),
            ("Import readable certificates", self.import_physical_card),
            ("Create proxy profile", self.create_proxy_profile),
        ):
            b = Gtk.Button(label=label)
            b.connect("clicked", cb)
            actions.pack_start(b, True, True, 0)

        note = Gtk.Label()
        note.set_markup(
            "<b>Duplication behavior:</b> public/readable objects can be copied. "
            "Protected private keys remain on the physical card; use proxy mode for full functionality."
        )
        note.set_line_wrap(True)
        note.set_xalign(0)
        box.pack_start(note, False, False, 0)

        frame = Gtk.Frame(label="Inspection")
        box.pack_start(frame, True, True, 0)

        self.physical_details = Gtk.TextView()
        self.physical_details.set_editable(False)
        self.physical_details.set_cursor_visible(False)
        sc = Gtk.ScrolledWindow()
        sc.add(self.physical_details)
        frame.add(sc)

        self.notebook.append_page(box, Gtk.Label(label="Physical Cards"))

    def build_diagnostics_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_border_width(8)

        row = Gtk.Box(spacing=6)
        box.pack_start(row, False, False, 0)

        for label, cb in (
            ("Refresh PC/SC", self.diag_pcsc),
            ("Initialize / repair PC/SC", self.initialize_pcsc_as_root),
            ("OpenSC readers", self.diag_opensc),
            ("Test software card", self.diag_software_card),
            ("vicc --help", self.diag_vicc),
        ):
            b = Gtk.Button(label=label)
            b.connect("clicked", cb)
            row.pack_start(b, True, True, 0)

        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_cursor_visible(False)
        sc = Gtk.ScrolledWindow()
        sc.add(self.log_view)
        box.pack_start(sc, True, True, 0)

        self.notebook.append_page(box, Gtk.Label(label="Diagnostics"))

    # -------------------------------------------------------------- profiles

    def profile_dirs(self):
        items = []
        for d in sorted(CARDS_DIR.iterdir()):
            if d.is_dir() and (d / "card.json").exists():
                items.append((d, load_json(d / "card.json", {})))
        return items

    def profile_by_id(self, profile_id):
        for d, meta in self.profile_dirs():
            if meta.get("id") == profile_id:
                return d, meta
        return None, None

    def active_profile(self):
        return self.profile_by_id(self.config.get("active_card"))

    def reader_profile(self, slot):
        pid = self.config.get("reader_profiles", {}).get(str(slot))
        return self.profile_by_id(pid)

    def _activate_reader_profile_for_edit(self, slot):
        """Make the reader-assigned profile the active library profile."""
        pdir, meta = self.reader_profile(slot)
        if not meta:
            self._info(f"Reader {slot + 1} does not have a certificate profile assigned.")
            return None, None

        pid = meta.get("id")
        self.config["active_card"] = pid
        save_json(CONFIG_FILE, self.config)
        if hasattr(self, "profile_combo"):
            self.profile_combo.set_active_id(pid)
        return pdir, meta

    def _profile_inserted_slots(self, profile_id):
        slots = []
        for slot in (0, 1):
            _d, meta = self.reader_profile(slot)
            if meta and meta.get("id") == profile_id and self.is_inserted(slot):
                slots.append(slot)
        return slots

    def _ensure_reader_profile_not_inserted(self, slot, action_name):
        _d, meta = self.reader_profile(slot)
        if not meta:
            self._info(f"Reader {slot + 1} does not have a certificate profile assigned.")
            return False
        used = self._profile_inserted_slots(meta.get("id"))
        if used:
            names = ", ".join(f"Reader {s + 1}" for s in used)
            self._error(
                f"Remove this profile from {names} before {action_name}.\\n\\n"
                "The running virtual card keeps its current credentials until it is removed."
            )
            return False
        return True

    def reader_set_pin(self, slot):
        if not self._ensure_reader_profile_not_inserted(slot, "changing its PIN"):
            return
        if self._activate_reader_profile_for_edit(slot)[1]:
            self.set_profile_pin()

    def reader_set_card_type(self, slot):
        if not self._ensure_reader_profile_not_inserted(slot, "changing its card type"):
            return
        if self._activate_reader_profile_for_edit(slot)[1]:
            self.set_profile_card_type()

    def reader_certificate_password(self, slot):
        if not self._ensure_reader_profile_not_inserted(slot, "changing its certificate password"):
            return
        if self._activate_reader_profile_for_edit(slot)[1]:
            self.manage_certificate_password()

    def on_reader_profile_changed(self, combo, slot):
        if getattr(self, "_refreshing_reader_combos", False):
            return
        pid = combo.get_active_id()
        self.config.setdefault("reader_profiles", {"0": None, "1": None})[str(slot)] = pid
        save_json(CONFIG_FILE, self.config)
        self.update_ui()

    def refresh_profiles(self):
        profiles = self.profile_dirs()
        self.profile_combo.remove_all()
        ids = []

        for d, meta in profiles:
            pid = meta.get("id", d.name)
            ids.append(pid)
            name = meta.get("name", d.name)
            mode = meta.get("mode", "software")
            self.profile_combo.append(pid, f"{name} [{mode}]")

        active = self.config.get("active_card")
        if active in ids:
            self.profile_combo.set_active_id(active)
        elif ids:
            self.config["active_card"] = ids[0]
            save_json(CONFIG_FILE, self.config)
            self.profile_combo.set_active_id(ids[0])

        # Refresh the profile assignment list for both virtual readers.
        if hasattr(self, "reader_profile_combos"):
            self._refreshing_reader_combos = True
            try:
                assignments = self.config.setdefault("reader_profiles", {"0": None, "1": None})
                for slot, combo in self.reader_profile_combos.items():
                    combo.remove_all()
                    combo.append(None, "— Select profile —")
                    for d, meta in profiles:
                        pid = meta.get("id", d.name)
                        name = meta.get("name", d.name)
                        card_type = meta.get("card_type", "piv").upper()
                        combo.append(pid, f"{name} [{card_type}]")
                    assigned = assignments.get(str(slot))
                    if assigned in ids:
                        combo.set_active_id(assigned)
                    else:
                        combo.set_active(0)
            finally:
                self._refreshing_reader_combos = False

        self.update_profile_details()

    def on_profile_changed(self, combo):
        pid = combo.get_active_id()
        if pid:
            self.config["active_card"] = pid
            save_json(CONFIG_FILE, self.config)
            self.update_profile_details()
            self.update_ui()

    def _profile_details_text(self, slot):
        pdir, meta = self.reader_profile(slot)
        state = "INSERTED" if self.is_inserted(slot) else "REMOVED"

        lines = [
            f"Reader {slot + 1}",
            "=" * 72,
            f"State:       {state}",
            f"PC/SC:       Virtual PCD 00 0{slot}",
        ]

        if not meta:
            lines += [
                "",
                "PROFILE",
                "-" * 72,
                "No certificate profile is assigned to this virtual reader.",
            ]
            return "\n".join(lines)

        lines += [
            "",
            "PROFILE",
            "-" * 72,
            f"Name:        {meta.get('name', '')}",
            f"Mode:        {meta.get('mode', 'software')}",
            f"Card type:   {meta.get('card_type', 'piv').upper()}",
            f"Profile ID:  {meta.get('id', '')}",
            f"Created:     {meta.get('created', '')}",
            f"PIN:         {'Configured' if meta.get('pin_configured') else 'NOT CONFIGURED'}",
        ]

        if meta.get("source_reader"):
            lines.append(f"Source:      {meta['source_reader']}")
        if meta.get("atr"):
            lines.append(f"ATR:         {meta['atr']}")

        certs = meta.get("certificates", [])
        lines += [
            "",
            f"CERTIFICATES ({len(certs)})",
            "-" * 72,
        ]

        if not certs:
            lines.append("No certificates available.")
        else:
            for idx, cert in enumerate(certs, start=1):
                ci = cert.get("info", {})
                lines.append(f"[{idx}] {cert.get('filename', '?')}")
                if ci.get("subject"):
                    lines.append(f"    Subject: {ci['subject']}")
                if ci.get("issuer"):
                    lines.append(f"    Issuer:  {ci['issuer']}")

                validity = certificate_validity(ci)
                lines.append(
                    f"    Validity: {validity['status']} ({validity['summary']})"
                )
                lines.append(
                    "    Valid from: "
                    + _format_cert_time(validity.get("not_before"), ci.get("notbefore"))
                )
                lines.append(
                    "    Expires:    "
                    + _format_cert_time(validity.get("not_after"), ci.get("notafter"))
                )

                alg = ci.get("public_key_algorithm")
                bits = ci.get("public_key_bits")
                if alg or bits:
                    key_text = " ".join(str(v) for v in (alg, bits) if v)
                    lines.append(f"    Key:       {key_text}")
                if ci.get("serial"):
                    lines.append(f"    Serial:    {ci['serial']}")
                fingerprint = ci.get("sha256_fingerprint") or ci.get("fingerprint")
                if fingerprint:
                    lines.append(f"    SHA-256:   {fingerprint}")
                if idx != len(certs):
                    lines.append("")

        if meta.get("pkcs12") or meta.get("private_key_file") or meta.get("private_key"):
            lines += [
                "",
                "KEY MATERIAL",
                "-" * 72,
            ]
            if meta.get("pkcs12"):
                stored = "stored" if meta.get("store_pkcs12_password") else "not stored"
                lines.append(f"PKCS#12:     {meta['pkcs12']}")
                lines.append(f"Password:    {stored}")
            if meta.get("private_key_file"):
                lines.append(f"Private key: {meta['private_key_file']}")
            elif meta.get("private_key"):
                lines.append(f"Private key: {meta['private_key']}")

        mode = meta.get("mode", "software")
        lines += [
            "",
            "SMARTCARD BACKEND",
            "-" * 72,
        ]

        if mode == "software":
            card_type = meta.get("card_type", "piv").lower()
            if card_type == "cac":
                lines += [
                    "Type:        CAC compatibility card via vpcd / pcscd",
                    "CAC ID AID:  A0000000790100",
                    "Certificate: Enabled",
                    "PIN VERIFY:  Enabled",
                    "RSA crypto:  Enabled when a usable private key is present",
                    "Scope:       CAC ID slot implemented",
                ]
            else:
                lines += [
                    "Type:        PIV-II card via vpcd / pcscd",
                    "Certificate: Enabled",
                    "PIN VERIFY:  Enabled",
                    "RSA crypto:  Enabled when a usable private key is present",
                ]
        elif mode == "snapshot":
            lines += [
                "Type:        Certificate-only PIV snapshot",
                "Private key: Not copied",
            ]
        elif mode == "proxy":
            lines += [
                "Type:        Physical smartcard APDU proxy",
                "Transport:   PC/SC relay",
            ]

        if not meta.get("pin_configured"):
            lines += [
                "",
                "WARNING",
                "-" * 72,
                "Virtual smartcard PIN is NOT CONFIGURED.",
                f"Use Reader {slot + 1} -> Set / change PIN before insertion.",
            ]

        return "\n".join(lines)

    def _apply_profile_detail_validity_tags(self, tv):
        """Color invalid certificate validity information without changing text."""
        buf = tv.get_buffer()
        table = buf.get_tag_table()
        tag = table.lookup("certificate-invalid")
        if tag is None:
            tag = buf.create_tag(
                "certificate-invalid",
                foreground="red",
                weight=700,
            )

        start = buf.get_start_iter()
        end = buf.get_end_iter()
        buf.remove_tag(tag, start, end)

        text_value = buf.get_text(start, end, True)
        lines = text_value.splitlines(True)
        offset = 0
        invalid = None

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("Validity:"):
                if "NOT YET VALID" in stripped:
                    invalid = "not-yet-valid"
                elif "EXPIRED" in stripped:
                    invalid = "expired"
                else:
                    invalid = None

                if invalid:
                    a = buf.get_iter_at_offset(offset)
                    b = buf.get_iter_at_offset(offset + len(line.rstrip("\n")))
                    buf.apply_tag(tag, a, b)

            elif invalid == "not-yet-valid" and stripped.startswith("Valid from:"):
                a = buf.get_iter_at_offset(offset)
                b = buf.get_iter_at_offset(offset + len(line.rstrip("\n")))
                buf.apply_tag(tag, a, b)
            elif invalid == "expired" and stripped.startswith("Expires:"):
                a = buf.get_iter_at_offset(offset)
                b = buf.get_iter_at_offset(offset + len(line.rstrip("\n")))
                buf.apply_tag(tag, a, b)

            offset += len(line)

    def update_profile_details(self):
        # Reader details are refreshed frequently by the health timer. Do not
        # rewrite the Gtk.TextBuffer unless its contents have actually changed:
        # set_text() resets the TextView's layout/scroll position and used to
        # make a reader profile jump back to the top every couple of seconds.
        if hasattr(self, "reader_profile_details"):
            for slot, tv in self.reader_profile_details.items():
                wanted = self._profile_details_text(slot)
                buf = tv.get_buffer()
                current = buf.get_text(
                    buf.get_start_iter(),
                    buf.get_end_iter(),
                    True,
                )
                if current != wanted:
                    # Preserve the native scroll position across a legitimate
                    # content update too (for example INSERTED -> REMOVED).
                    parent = tv.get_parent()
                    scrolled = parent if isinstance(parent, Gtk.ScrolledWindow) else None
                    vadj = scrolled.get_vadjustment() if scrolled else None
                    old_value = vadj.get_value() if vadj else 0.0

                    buf.set_text(wanted)
                    self._apply_profile_detail_validity_tags(tv)

                    if vadj:
                        def restore_scroll(adj=vadj, value=old_value):
                            upper = adj.get_upper()
                            page = adj.get_page_size()
                            adj.set_value(max(adj.get_lower(), min(value, upper - page)))
                            return False
                        GLib.idle_add(restore_scroll)
                else:
                    self._apply_profile_detail_validity_tags(tv)

    def _available_card_types(self):
        """
        Return card personalities currently implemented by the app.

        Built-in personalities live in CARD_TYPE_REGISTRY. Future virtual-card
        backends/drivers can append entries to this registry during startup,
        which makes the Card type dialog automatically expose them without
        needing a new widget implementation.
        """
        seen = set()
        result = []
        for item in CARD_TYPE_REGISTRY:
            cid = str(item.get("id", "")).strip().lower()
            if not cid or cid in seen:
                continue
            seen.add(cid)
            result.append({
                "id": cid,
                "label": str(item.get("label", cid.upper())),
                "description": str(item.get("description", "")).strip(),
            })
        return result

    def _ask_card_type(self, current="piv", title="Set virtual smartcard type"):
        card_types = self._available_card_types()
        if not card_types:
            self._error("No virtual smartcard types are currently available.")
            return None

        valid_ids = {item["id"] for item in card_types}
        if current not in valid_ids:
            current = card_types[0]["id"]

        d = Gtk.Dialog(title=title, parent=self.window)
        d.set_modal(True)
        d.set_transient_for(self.window)
        d.set_resizable(False)
        d.set_default_size(480, -1)
        d.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK,
        )
        d.set_default_response(Gtk.ResponseType.OK)

        box = d.get_content_area()
        box.set_spacing(10)
        box.set_border_width(12)

        heading = Gtk.Label()
        heading.set_markup("<b>Select the virtual smartcard type</b>")
        heading.set_xalign(0)
        box.pack_start(heading, False, False, 0)

        intro = Gtk.Label(
            label=(
                "Choose the smartcard interface this certificate should expose. "
                "Only card types currently implemented by IGEL Virtual Smartcard "
                "are shown."
            )
        )
        intro.set_line_wrap(True)
        intro.set_max_width_chars(64)
        intro.set_xalign(0)
        box.pack_start(intro, False, False, 0)

        options_frame = Gtk.Frame()
        box.pack_start(options_frame, False, False, 0)
        options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        options_box.set_border_width(10)
        options_frame.add(options_box)

        radio_by_id = {}
        first_radio = None

        for item in card_types:
            row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

            if first_radio is None:
                radio = Gtk.RadioButton.new_with_label_from_widget(
                    None, item["label"]
                )
                first_radio = radio
            else:
                radio = Gtk.RadioButton.new_with_label_from_widget(
                    first_radio, item["label"]
                )

            radio_by_id[item["id"]] = radio
            row.pack_start(radio, False, False, 0)

            if item["description"]:
                desc = Gtk.Label(label=item["description"])
                desc.set_line_wrap(True)
                desc.set_max_width_chars(58)
                desc.set_xalign(0)
                desc.set_margin_start(26)
                row.pack_start(desc, False, False, 0)

            options_box.pack_start(row, False, False, 0)

        radio_by_id[current].set_active(True)

        note = Gtk.Label(
            label=(
                "Changing card type changes the protocol personality presented "
                "to middleware; it does not modify the certificate itself."
            )
        )
        note.set_line_wrap(True)
        note.set_max_width_chars(64)
        note.set_xalign(0)
        box.pack_start(note, False, False, 0)

        d.show_all()

        # Keep the dialog inside the main application's footprint as much as
        # the window manager allows, rather than expanding to screen width.
        try:
            _x, _y, app_w, _app_h = self.window.get_allocation()
            target_w = min(520, max(420, app_w - 80))
            d.resize(target_w, 1)
        except Exception:
            pass

        response = d.run()
        value = None
        if response == Gtk.ResponseType.OK:
            for cid, radio in radio_by_id.items():
                if radio.get_active():
                    value = cid
                    break

        d.destroy()
        return value

    def set_profile_card_type(self, *_):
        pdir, meta = self.active_profile()
        if not meta:
            return
        if meta.get("mode", "software") != "software":
            self._info("Card type selection applies to software certificate profiles.")
            return
        inserted_slots = self._profile_inserted_slots(meta.get("id"))
        if inserted_slots:
            names = ", ".join(f"Reader {s + 1}" for s in inserted_slots)
            self._error(f"Remove this profile from {names} before changing its card type.")
            return

        current = meta.get("card_type", "piv").lower()
        value = self._ask_card_type(current=current, title="Set virtual smartcard type")
        if value is None:
            return
        meta["card_type"] = value
        save_json(pdir / "card.json", meta)
        self.log(f"Card type for {meta.get('name', 'profile')} changed to {value.upper()}")
        self.update_profile_details()
        self.update_ui()

    def set_profile_pin(self, *_):
        pdir, meta = self.active_profile()
        if not meta:
            return

        pin = self._ask_virtual_pin("Set Virtual Smartcard PIN")
        if pin is None:
            return

        try:
            self._store_virtual_pin(pdir, meta, pin)
            save_json(pdir / "card.json", meta)
            self.log(f"Virtual smartcard PIN configured for {meta.get('name', 'profile')}")
            self.update_profile_details()
            self.update_ui()
        except Exception as exc:
            self._error(f"Could not store virtual smartcard PIN:\n{exc}")

    def manage_certificate_password(self, *_):
        pdir, meta = self.active_profile()
        if not meta or not meta.get("pkcs12"):
            self._info("The selected profile does not contain a PFX/P12 file.")
            return

        d = Gtk.Dialog(title="Certificate password", parent=self.window)
        d.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK,
        )
        box = d.get_content_area()
        box.set_spacing(8)

        entry = Gtk.Entry()
        entry.set_visibility(False)
        entry.set_invisible_char("•")

        stored = bool(meta.get("store_pkcs12_password"))
        if stored:
            try:
                secret_path = pdir / meta.get("pkcs12_password_file", "")
                if secret_path.exists():
                    current = decrypt_secret(
                        json.loads(secret_path.read_text(encoding="utf-8"))
                    )
                    entry.set_text(current)
            except Exception:
                pass

        box.pack_start(Gtk.Label(label="Certificate/PFX password:"), False, False, 2)
        box.pack_start(entry, False, False, 2)

        store = Gtk.CheckButton(label="Store certificate password")
        store.set_active(stored if "store_pkcs12_password" in meta else True)
        box.pack_start(store, False, False, 2)

        d.show_all()
        if d.run() == Gtk.ResponseType.OK:
            password = entry.get_text()
            if store.get_active():
                if not password:
                    self._error("Enter the certificate password before enabling storage.")
                    d.destroy()
                    return
                try:
                    self._store_pkcs12_password(pdir, meta, password)
                except Exception as exc:
                    self._error(f"Could not store certificate password:\n{exc}")
                    d.destroy()
                    return
            else:
                self._remove_stored_pkcs12_password(pdir, meta)

            save_json(pdir / "card.json", meta)
            self.update_profile_details()

        d.destroy()

    def _validate_virtual_pin(self, pin):
        if not re.fullmatch(r"[0-9]{6,8}", pin or ""):
            return False, "PIN must contain 6 to 8 numeric digits."
        return True, ""

    def _ask_virtual_pin(self, title="Virtual Smartcard PIN"):
        """
        Require a 6-8 digit numeric PIN and confirmation.
        """
        while True:
            d = Gtk.Dialog(title=title, parent=self.window)
            d.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK, Gtk.ResponseType.OK,
            )
            box = d.get_content_area()
            box.set_spacing(8)

            heading = Gtk.Label()
            heading.set_markup(
                "<b>Assign the PIN for this virtual smartcard</b>\n"
                "The PIN must be 6 to 8 numeric digits."
            )
            heading.set_xalign(0)
            box.pack_start(heading, False, False, 2)

            grid = Gtk.Grid(column_spacing=8, row_spacing=8)
            box.pack_start(grid, False, False, 2)

            pin_entry = Gtk.Entry()
            pin_entry.set_visibility(False)
            pin_entry.set_invisible_char("•")
            confirm_entry = Gtk.Entry()
            confirm_entry.set_visibility(False)
            confirm_entry.set_invisible_char("•")

            grid.attach(Gtk.Label(label="PIN:"), 0, 0, 1, 1)
            grid.attach(pin_entry, 1, 0, 1, 1)
            grid.attach(Gtk.Label(label="Confirm PIN:"), 0, 1, 1, 1)
            grid.attach(confirm_entry, 1, 1, 1, 1)

            example = Gtk.Label()
            example.set_markup("<small>Example: 123456</small>")
            example.set_xalign(0)
            box.pack_start(example, False, False, 2)

            d.show_all()
            response = d.run()

            if response != Gtk.ResponseType.OK:
                d.destroy()
                return None

            pin = pin_entry.get_text()
            confirm = confirm_entry.get_text()
            d.destroy()

            valid, reason = self._validate_virtual_pin(pin)
            if not valid:
                self._error(reason)
                continue

            if pin != confirm:
                self._error("PIN and confirmation do not match.")
                continue

            return pin

    def _store_virtual_pin(self, pdir, meta, pin):
        valid, reason = self._validate_virtual_pin(pin)
        if not valid:
            raise ValueError(reason)

        secret_file = pdir / "virtual-pin.enc.json"
        secret_file.write_text(
            json.dumps(encrypt_secret(pin), indent=2) + "\n",
            encoding="utf-8",
        )
        os.chmod(secret_file, 0o600)

        meta.pop("pin", None)  # remove legacy plaintext PIN
        meta["pin_configured"] = True
        meta["pin_secret_file"] = secret_file.name

    def _remove_virtual_pin(self, pdir, meta):
        secret_name = meta.pop("pin_secret_file", None)
        meta.pop("pin", None)
        meta["pin_configured"] = False
        if secret_name:
            try:
                (pdir / secret_name).unlink()
            except FileNotFoundError:
                pass

    # --------------------------------------------------------------- imports

    def import_files(self, *_):
        chooser = Gtk.FileChooserDialog(
            title="Import certificate, key or PKCS#12",
            parent=self.window,
            action=Gtk.FileChooserAction.OPEN,
        )
        chooser.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        chooser.set_select_multiple(True)

        flt = Gtk.FileFilter()
        flt.set_name("Certificates and keys")
        for pat in ("*.pem", "*.crt", "*.cer", "*.der", "*.key", "*.p12", "*.pfx"):
            flt.add_pattern(pat)
        chooser.add_filter(flt)

        if chooser.run() == Gtk.ResponseType.OK:
            files = [Path(x) for x in chooser.get_filenames()]
            chooser.destroy()
            self._import_selected_files(files)
        else:
            chooser.destroy()

    def _import_selected_files(self, files):
        if not files:
            return

        name = self._ask_text(
            "Card profile name",
            "Name for this virtual card:",
            files[0].stem,
        )
        if name is None:
            return

        card_type = self._ask_card_type(current="piv", title="Choose Virtual Smartcard Type")
        if card_type is None:
            return

        virtual_pin = self._ask_virtual_pin("Assign Virtual Smartcard PIN")
        if virtual_pin is None:
            return

        pid = uuid.uuid4().hex
        pdir = CARDS_DIR / f"{slugify(name)}-{pid[:8]}"
        pdir.mkdir(mode=0o700)

        meta = {
            "id": pid,
            "name": name,
            "mode": "software",
            "card_type": card_type,
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
            "piv_guid": uuid.uuid4().hex,
            "certificates": [],
            "pin_configured": False,
        }

        self._store_virtual_pin(pdir, meta, virtual_pin)

        for src in files:
            ext = src.suffix.lower()
            dst = pdir / src.name
            safe_copy(src, dst)

            if ext in (".crt", ".cer", ".der", ".pem"):
                ci = cert_info(dst)
                if not ci.get("error"):
                    meta["certificates"].append({"filename": dst.name, "info": ci})
                    continue

                # A PEM file may instead be a private key.
                rc, _ = run_cmd(["openssl", "pkey", "-in", str(dst), "-noout"])
                if rc == 0:
                    meta["private_key_file"] = dst.name

            elif ext == ".key":
                meta["private_key_file"] = dst.name

            elif ext in (".p12", ".pfx"):
                meta["pkcs12"] = dst.name
                self._inspect_pkcs12(pdir, dst, meta)

        save_json(pdir / "card.json", meta)
        self.config["active_card"] = pid
        save_json(CONFIG_FILE, self.config)
        self.refresh_profiles()
        self.log(f"Imported software profile '{name}'")

    def _ask_pkcs12_password(self, filename):
        """
        Ask for the PFX/P12 password and whether to store it.
        Storage is enabled by default as requested.
        """
        d = Gtk.Dialog(title="PKCS#12 password", parent=self.window)
        d.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK,
        )

        box = d.get_content_area()
        box.set_spacing(8)

        label = Gtk.Label(label=f"Password for {filename}:")
        label.set_xalign(0)
        box.pack_start(label, False, False, 2)

        entry = Gtk.Entry()
        entry.set_visibility(False)
        entry.set_invisible_char("•")
        box.pack_start(entry, False, False, 2)

        store = Gtk.CheckButton(label="Store certificate password")
        store.set_active(True)
        store.set_tooltip_text(
            "Stores the password encrypted under ~/.config/igelvsc so the "
            "virtual card can be inserted without asking again."
        )
        box.pack_start(store, False, False, 2)

        note = Gtk.Label()
        note.set_markup(
            "<small>The password is encrypted locally and the secret files are "
            "restricted to the current user.</small>"
        )
        note.set_line_wrap(True)
        note.set_xalign(0)
        box.pack_start(note, False, False, 2)

        d.show_all()
        if d.run() != Gtk.ResponseType.OK:
            d.destroy()
            return None, False

        password = entry.get_text()
        should_store = store.get_active()
        d.destroy()
        return password, should_store

    def _store_pkcs12_password(self, pdir, meta, password):
        secret_file = pdir / "pkcs12-password.enc.json"
        blob = encrypt_secret(password)
        secret_file.write_text(json.dumps(blob, indent=2) + "\n", encoding="utf-8")
        os.chmod(secret_file, 0o600)

        meta["store_pkcs12_password"] = True
        meta["pkcs12_password_file"] = secret_file.name

    def _remove_stored_pkcs12_password(self, pdir, meta):
        secret_name = meta.pop("pkcs12_password_file", None)
        meta["store_pkcs12_password"] = False
        if secret_name:
            secret_path = pdir / secret_name
            try:
                secret_path.unlink()
            except FileNotFoundError:
                pass

    def _inspect_pkcs12(self, pdir, pfx_path, meta):
        password, should_store = self._ask_pkcs12_password(pfx_path.name)
        if password is None:
            self.log("PKCS#12 stored without inspection.")
            meta["store_pkcs12_password"] = False
            return

        cert_out = pdir / "certificate-from-pkcs12.pem"
        rc, out = run_cmd([
            "openssl", "pkcs12",
            "-in", str(pfx_path),
            "-clcerts", "-nokeys",
            "-passin", f"pass:{password}",
            "-out", str(cert_out),
        ])

        if rc != 0:
            self.log("PKCS#12 certificate extraction failed: " + out.strip())
            meta["store_pkcs12_password"] = False
            return

        if cert_out.exists():
            os.chmod(cert_out, 0o600)
            meta["certificates"].append({
                "filename": cert_out.name,
                "info": cert_info(cert_out),
            })
            meta["pkcs12_contains_private_key"] = True

        if should_store:
            try:
                self._store_pkcs12_password(pdir, meta, password)
                self.log("PKCS#12 password stored for automatic insertion.")
            except Exception as exc:
                self.log(f"Could not store PKCS#12 password: {exc}")
                meta["store_pkcs12_password"] = False
        else:
            self._remove_stored_pkcs12_password(pdir, meta)

    # --------------------------------------------------------------- readers

    def _runtime_vpcd_driver_path(self):
        if PACKAGED_VPCD_DRIVER.exists():
            return PACKAGED_VPCD_DRIVER
        if PACKAGED_VPCD_DRIVER_REAL.exists():
            return PACKAGED_VPCD_DRIVER_REAL
        return None

    def prepare_runtime_vpcd_config(self):
        """
        Create a writable reader.conf.d entry below the *logged-in user's*
        ~/.config/igelvsc tree and point LIBPATH at the Recipe Studio service.
        """
        driver = self._runtime_vpcd_driver_path()
        if driver is None:
            raise RuntimeError(
                "Packaged vpcd driver not found under "
                "/services/igelvirtualsmartcard/usr/lib/pcsc/drivers/serial/"
            )

        if not PACKAGED_VPCD_CONF.exists():
            raise RuntimeError(
                f"Packaged vpcd configuration not found: {PACKAGED_VPCD_CONF}"
            )

        raw = PACKAGED_VPCD_CONF.read_text(encoding="utf-8", errors="replace")
        lines = []
        replaced = False
        for line in raw.splitlines():
            if line.lstrip().startswith("LIBPATH"):
                lines.append(f"LIBPATH      {driver}")
                replaced = True
            else:
                lines.append(line)
        if not replaced:
            lines.append(f"LIBPATH      {driver}")

        RUNTIME_READER_DIR.mkdir(parents=True, exist_ok=True)

        # Preserve existing system reader.conf.d definitions so taking over
        # pcscd for Virtual PCD does not hide a physical reader that depends on
        # a serial/static reader configuration. USB CCID readers continue to be
        # discovered by pcscd's normal USB driver directory.
        system_reader_dir = Path("/etc/reader.conf.d")
        if system_reader_dir.is_dir():
            for source in system_reader_dir.iterdir():
                if not source.is_file() or source.name == "vpcd":
                    continue
                try:
                    target = RUNTIME_READER_DIR / f"system-{source.name}"
                    target.write_bytes(source.read_bytes())
                    os.chmod(target, 0o600)
                except Exception as exc:
                    self.log(f"Could not preserve system reader config {source}: {exc}")

        RUNTIME_VPCD_CONF.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.chmod(RUNTIME_VPCD_CONF, 0o600)

        self.log(f"Generated runtime PC/SC config: {RUNTIME_VPCD_CONF}")
        self.log(f"vpcd driver: {driver}")
        return driver

    def _probe_pcsc_fresh(self):
        """
        Probe PC/SC in a brand-new Python process.

        This is intentional. If pcscd is stopped/restarted, an already-loaded
        pyscard context in this GUI process can remain stale and keep returning
        SCARD_E_NO_SERVICE even though a fresh process sees the readers.
        """
        code = r"""
from smartcard.System import readers
try:
    rs = list(readers())
    for i, r in enumerate(rs):
        print(f"{i}\t{r}")
except Exception as e:
    print("ERROR\t" + str(e))
    raise
"""
        try:
            p = subprocess.run(
                [sys.executable, "-c", code],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=8,
                check=False,
            )
        except Exception as exc:
            return False, [], str(exc)

        entries = []
        error = None
        for line in p.stdout.splitlines():
            if line.startswith("ERROR\t"):
                error = line.split("\t", 1)[1]
                continue
            if "\t" in line:
                idx, name = line.split("\t", 1)
                try:
                    entries.append({"pcsc_index": int(idx), "name": name})
                except ValueError:
                    pass

        return p.returncode == 0, entries, error or p.stdout.strip()

    def _fresh_virtual_reader_names(self):
        ok, entries, detail = self._probe_pcsc_fresh()
        if not ok:
            return [], detail
        return [x["name"] for x in entries if "Virtual PCD" in x["name"]], detail

    def _su_root_popen(self, shell_command, log_path):
        """
        IGEL OS supports privileged execution from the user session with:
            su -c "<command>" root

        Keep the main GUI as the normal user and elevate only the PC/SC helper.
        """
        log_handle = open(log_path, "ab", buffering=0)
        return subprocess.Popen(
            ["su", "-c", shell_command, "root"],
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

    def _start_custom_pcscd(self):
        self.prepare_runtime_vpcd_config()

        pcscd_bin = shutil.which("pcscd") or "/sbin/pcscd"
        log_path = LOG_DIR / "pcscd.log"

        # One privileged command stops the stock socket/service and starts the
        # custom daemon in the foreground using the user's generated config.
        command = (
            "systemctl stop pcscd.socket pcscd.service 2>/dev/null || true; "
            "pkill -x pcscd 2>/dev/null || true; "
            f"exec {pcscd_bin} --foreground --config '{RUNTIME_READER_DIR}'"
        )

        self.log("Starting IGEL PC/SC helper using: su -c <pcscd command> root")
        self.pcscd_process = self._su_root_popen(command, log_path)

        # IMPORTANT: use fresh-process probes while pcscd is being replaced.
        deadline = time.time() + 8.0
        last_detail = ""
        while time.time() < deadline:
            time.sleep(0.35)

            names, detail = self._fresh_virtual_reader_names()
            last_detail = detail
            if names:
                self.log("PC/SC ready: " + ", ".join(names))

                # We deliberately have not imported pyscard in this GUI process
                # during the restart path. It is now safe to enumerate normally.
                self.refresh_readers()
                return True

            if self.pcscd_process.poll() is not None:
                break

        if self.pcscd_process.poll() is not None:
            raise RuntimeError(
                f"Privileged PC/SC helper exited with status "
                f"{self.pcscd_process.returncode}. See {log_path}"
            )

        raise RuntimeError(
            "pcscd started but fresh PC/SC probes did not see Virtual PCD. "
            f"Last probe: {last_detail}. See {log_path}"
        )

    def ensure_virtual_readers(self, interactive=True):
        """
        First check using a *fresh* client process to avoid stale pyscard state.
        If Virtual PCD is absent, initialize the packaged driver through
        `su -c ... root`, while the GUI remains the normal IGEL user.
        """
        names, detail = self._fresh_virtual_reader_names()
        if names:
            self.refresh_readers()
            return True

        try:
            return self._start_custom_pcscd()
        except Exception as exc:
            self.log(f"PC/SC initialization failed: {exc}")
            if interactive:
                self._error(f"Could not initialize Virtual PCD:\n{exc}")
            return False

    def initialize_pcsc_as_root(self, *_):
        """
        Kept as a Diagnostics action, but it now works from the ordinary IGEL
        user session using the IGEL-supported `su -c ... root` mechanism.
        """
        if self.ensure_virtual_readers(interactive=True):
            self.update_ui()

    def _physical_reader_summary(self, entry):
        """
        Lightweight live summary for the Reader details notebook.

        This intentionally avoids pkcs15-tool on the 2-second health-check path.
        Full OpenSC inspection remains available from the Physical Cards tab.
        """
        lines = [
            f"Reader: {entry.get('name', '')}",
            f"PC/SC index: {entry.get('pcsc_index', '')}",
        ]

        try:
            conn = entry["reader"].createConnection()
            conn.connect()
            atr = bytes(conn.getATR()).hex(" ").upper()
            lines += [
                "State: CARD INSERTED",
                f"ATR: {atr}",
                "",
                "The physical card is available through the same PC/SC service as the virtual readers.",
                "Use the Physical Cards tab for OpenSC/PKCS#15 certificate and key inspection.",
            ]
        except Exception as exc:
            msg = str(exc)
            # Empty-reader errors differ between pcsc-lite/pyscard versions.
            lines += [
                "State: NO CARD / NOT CONNECTABLE",
                f"PC/SC status: {msg}",
                "",
                "Insert a physical smartcard and press Refresh in the Physical Cards tab.",
            ]

        return "\n".join(lines)

    def _rebuild_reader_detail_tabs(self):
        """
        Keep the first two notebook pages for Virtual Reader 1/2 and append one
        dynamic page for every physical PC/SC reader currently detected.

        Rebuild only when the reader set changes so native scrolling in a
        physical-reader detail page is not reset by the periodic health check.
        """
        if not hasattr(self, "reader_details_notebook"):
            return

        signature = tuple(
            (entry.get("name", ""), entry.get("pcsc_index"))
            for entry in self.physical_readers
        )
        if signature == self._physical_reader_tabs_signature:
            # Update the text only when it actually changed, preserving scroll.
            for idx, entry in enumerate(self.physical_readers):
                tv = self.physical_reader_detail_views.get(idx)
                if not tv:
                    continue
                wanted = self._physical_reader_summary(entry)
                buf = tv.get_buffer()
                current = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True)
                if current != wanted:
                    scrolled = tv.get_parent()
                    vadj = scrolled.get_vadjustment() if isinstance(scrolled, Gtk.ScrolledWindow) else None
                    old_value = vadj.get_value() if vadj else 0.0
                    buf.set_text(wanted)
                    if vadj:
                        def restore_scroll(adj=vadj, value=old_value):
                            upper = adj.get_upper()
                            page = adj.get_page_size()
                            adj.set_value(max(adj.get_lower(), min(value, upper - page)))
                            return False
                        GLib.idle_add(restore_scroll)
            return

        self._physical_reader_tabs_signature = signature
        nb = self.reader_details_notebook

        # Remove previously generated physical-reader pages.
        while nb.get_n_pages() > 2:
            nb.remove_page(2)

        self.physical_reader_detail_views = {}

        for idx, entry in enumerate(self.physical_readers, start=1):
            outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            outer.set_border_width(6)

            heading = Gtk.Label()
            heading.set_xalign(0)
            heading.set_markup(
                f"<b>Physical Reader {idx}</b> — "
                f"{GLib.markup_escape_text(entry.get('name', ''))}"
            )
            outer.pack_start(heading, False, False, 0)

            tv = Gtk.TextView()
            tv.set_editable(False)
            tv.set_cursor_visible(False)
            tv.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            tv.set_left_margin(8)
            tv.set_right_margin(8)
            tv.set_top_margin(8)
            tv.set_bottom_margin(8)
            try:
                from gi.repository import Pango
                tv.modify_font(Pango.FontDescription("Monospace 10"))
            except Exception:
                pass
            tv.get_buffer().set_text(self._physical_reader_summary(entry))

            sc = Gtk.ScrolledWindow()
            sc.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            sc.add(tv)
            outer.pack_start(sc, True, True, 0)

            self.physical_reader_detail_views[idx - 1] = tv
            nb.append_page(
                outer,
                Gtk.Label(label=f"Physical Reader {idx} profile")
            )

        nb.show_all()

    def refresh_readers(self):
        self.reader_combo.remove_all()
        self.physical_readers = []
        self.vpcd_readers = []

        try:
            from smartcard.System import readers
            all_readers = list(readers())

            for pcsc_index, reader in enumerate(all_readers):
                name = str(reader)
                entry = {
                    "pcsc_index": pcsc_index,
                    "reader": reader,
                    "name": name,
                }
                if "Virtual PCD" in name:
                    self.vpcd_readers.append(entry)
                else:
                    self.physical_readers.append(entry)
                    self.reader_combo.append_text(f"{pcsc_index}: {name}")

            if self.physical_readers:
                self.reader_combo.set_active(0)

        except Exception as exc:
            self.log(f"PC/SC reader enumeration failed: {exc}")

        self._rebuild_reader_detail_tabs()
        self.update_pcsc_label()

    def update_pcsc_label(self):
        if self.vpcd_readers:
            names = ", ".join(x["name"] for x in self.vpcd_readers)
            self.pcsc_label.set_markup(
                f"<span foreground='green'><b>PC/SC: {len(self.vpcd_readers)} Virtual PCD reader(s)</b></span>"
            )
            self.pcsc_label.set_tooltip_text(names)
        else:
            self.pcsc_label.set_markup(
                "<span foreground='red'><b>PC/SC: Virtual PCD missing</b></span>"
            )
            self.pcsc_label.set_tooltip_text(
                "vsmartcard-vpcd must be loaded by pcscd before software cards can be inserted."
            )

    def log_pcsc_state(self):
        if self.vpcd_readers:
            for r in self.vpcd_readers:
                self.log(f"pcscd reader available: {r['name']}")
        else:
            self.log("WARNING: no Virtual PCD reader is currently exposed by pcscd.")

    def selected_reader(self):
        idx = self.reader_combo.get_active()
        if idx < 0 or idx >= len(self.physical_readers):
            return None
        return self.physical_readers[idx]

    # --------------------------------------------------------- physical card

    def inspect_physical_card(self, *_):
        r = self.selected_reader()
        if not r:
            self._error("No physical reader selected.")
            return

        lines = [f"Reader: {r['name']}", f"PC/SC index: {r['pcsc_index']}"]

        try:
            conn = r["reader"].createConnection()
            conn.connect()
            atr = bytes(conn.getATR()).hex(" ").upper()
            lines.append(f"ATR: {atr}")
        except Exception as exc:
            lines.append(f"Card connection failed: {exc}")
            self.physical_details.get_buffer().set_text("\n".join(lines))
            return

        if shutil.which("pkcs15-tool"):
            for title, args in (
                ("PKCS#15 info", ["pkcs15-tool", "--reader", str(r["pcsc_index"]), "--list-info"]),
                ("Certificates", ["pkcs15-tool", "--reader", str(r["pcsc_index"]), "--list-certificates"]),
                ("Private keys - metadata only", ["pkcs15-tool", "--reader", str(r["pcsc_index"]), "--list-keys"]),
                ("Public keys", ["pkcs15-tool", "--reader", str(r["pcsc_index"]), "--list-public-keys"]),
                ("PINs - metadata only", ["pkcs15-tool", "--reader", str(r["pcsc_index"]), "--list-pins"]),
            ):
                rc, out = run_cmd(args, timeout=15)
                lines += ["", f"=== {title} ===", out.strip() or f"(exit {rc}, no output)"]

        self.physical_details.get_buffer().set_text("\n".join(lines))
        self.log(f"Inspected physical card in {r['name']}")

    def _pkcs15_cert_ids(self, reader_index):
        rc, out = run_cmd(
            ["pkcs15-tool", "--reader", str(reader_index), "--list-certificates"],
            timeout=20,
        )
        ids = []
        if rc == 0:
            for line in out.splitlines():
                m = re.match(r"\s*ID\s*:\s*([0-9A-Fa-f]+)\s*$", line)
                if m and m.group(1) not in ids:
                    ids.append(m.group(1))
        return ids, out

    def import_physical_card(self, *_):
        r = self.selected_reader()
        if not r:
            self._error("No physical reader selected.")
            return

        try:
            conn = r["reader"].createConnection()
            conn.connect()
            atr = bytes(conn.getATR()).hex(" ").upper()
        except Exception as exc:
            self._error(f"Could not connect to card:\n{exc}")
            return

        virtual_pin = self._ask_virtual_pin("Assign PIN for Imported Snapshot")
        if virtual_pin is None:
            return

        pid = uuid.uuid4().hex
        name = f"Snapshot - {r['name']}"
        pdir = CARDS_DIR / f"physical-{pid[:8]}"
        pdir.mkdir(mode=0o700)

        meta = {
            "id": pid,
            "name": name,
            "mode": "snapshot",
            "card_type": "piv",
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
            "piv_guid": uuid.uuid4().hex,
            "source_reader": r["name"],
            "source_reader_index": r["pcsc_index"],
            "atr": atr,
            "certificates": [],
            "private_key": "not copied; hardware protection preserved",
            "pin_configured": False,
        }

        self._store_virtual_pin(pdir, meta, virtual_pin)

        ids, listing = self._pkcs15_cert_ids(r["pcsc_index"])
        (pdir / "pkcs15-certificates.txt").write_text(listing, encoding="utf-8")

        for cid in ids:
            outfile = pdir / f"cert-{cid}.pem"
            rc, _ = run_cmd([
                "pkcs15-tool",
                "--reader", str(r["pcsc_index"]),
                "--read-certificate", cid,
                "--output", str(outfile),
            ])
            if rc == 0 and outfile.exists():
                os.chmod(outfile, 0o600)
                meta["certificates"].append({
                    "id": cid,
                    "filename": outfile.name,
                    "info": cert_info(outfile),
                })

        for fname, args in (
            ("pkcs15-info.txt", ["pkcs15-tool", "--reader", str(r["pcsc_index"]), "--list-info"]),
            ("pkcs15-keys.txt", ["pkcs15-tool", "--reader", str(r["pcsc_index"]), "--list-keys"]),
            ("pkcs15-public-keys.txt", ["pkcs15-tool", "--reader", str(r["pcsc_index"]), "--list-public-keys"]),
            ("pkcs15-pins.txt", ["pkcs15-tool", "--reader", str(r["pcsc_index"]), "--list-pins"]),
        ):
            rc, out = run_cmd(args)
            (pdir / fname).write_text(out, encoding="utf-8")
            os.chmod(pdir / fname, 0o600)

        save_json(pdir / "card.json", meta)
        self.config["active_card"] = pid
        save_json(CONFIG_FILE, self.config)
        self.refresh_profiles()
        self._info(
            f"Imported {len(meta['certificates'])} readable certificate(s).\n\n"
            "Protected private key material was not copied. "
            "This snapshot can be exposed as a certificate-only virtual PIV card."
        )

    def create_proxy_profile(self, *_):
        r = self.selected_reader()
        if not r:
            self._error("No physical reader selected.")
            return

        try:
            conn = r["reader"].createConnection()
            conn.connect()
            atr = bytes(conn.getATR()).hex(" ").upper()
        except Exception as exc:
            self._error(f"Could not connect to card:\n{exc}")
            return

        pid = uuid.uuid4().hex
        pdir = CARDS_DIR / f"proxy-{pid[:8]}"
        pdir.mkdir(mode=0o700)

        meta = {
            "id": pid,
            "name": f"Proxy - {r['name']}",
            "mode": "proxy",
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source_reader": r["name"],
            "source_reader_index": r["pcsc_index"],
            "atr": atr,
            "certificates": [],
        }

        ids, _ = self._pkcs15_cert_ids(r["pcsc_index"])
        for cid in ids:
            outfile = pdir / f"cert-{cid}.pem"
            rc, _ = run_cmd([
                "pkcs15-tool",
                "--reader", str(r["pcsc_index"]),
                "--read-certificate", cid,
                "--output", str(outfile),
            ])
            if rc == 0 and outfile.exists():
                os.chmod(outfile, 0o600)
                meta["certificates"].append({
                    "id": cid,
                    "filename": outfile.name,
                    "info": cert_info(outfile),
                })

        save_json(pdir / "card.json", meta)
        self.config["active_card"] = pid
        save_json(CONFIG_FILE, self.config)
        self.refresh_profiles()
        self.log(f"Created proxy profile for {r['name']}")

    # ------------------------------------------------------------- insertion

    def is_inserted(self, slot=None):
        if slot is None:
            return any(b is not None and b.running for b in self.software_backends.values()) or (
                self.vicc_process is not None and self.vicc_process.poll() is None
            )
        backend = self.software_backends.get(int(slot))
        if backend is not None and backend.running:
            return True
        # Physical relay remains bound to reader 1 / slot 0 in v0.4.2.
        if int(slot) == 0 and self.vicc_process is not None and self.vicc_process.poll() is None:
            return True
        return False

    def _save_dual_state(self):
        readers = {}
        for slot in (0, 1):
            backend = self.software_backends.get(slot)
            pdir, meta = self.reader_profile(slot)
            readers[str(slot)] = {
                "inserted": bool(backend is not None and backend.running) or (
                    slot == 0 and self.vicc_process is not None and self.vicc_process.poll() is None
                ),
                "profile_id": meta.get("id") if meta else None,
                "vpcd_port": VPCD_PORTS[slot],
            }
        self.state = {"readers": readers}
        save_json(STATE_FILE, self.state)

    def insert_card(self, *args, slot=0):
        slot = int(slot)
        if slot not in (0, 1):
            self._error("Invalid virtual reader slot.")
            return False

        if self.is_inserted(slot):
            self.log(f"Reader {slot + 1} already has a card inserted.")
            return False

        if not self.ensure_virtual_readers(interactive=True):
            return False

        pdir, meta = self.reader_profile(slot)
        if not meta:
            self._error(f"Select a profile for Virtual Reader {slot + 1} first.")
            return False

        mode = meta.get("mode", "software")
        if mode == "proxy":
            if slot != 0:
                self._error(
                    "Physical-card proxy profiles currently use Virtual Reader 1 only.\n\n"
                    "PIV/CAC software profiles can use either reader simultaneously."
                )
                return False
            return self._insert_proxy(pdir, meta)

        if not meta.get("pin_configured") or not meta.get("pin_secret_file"):
            self._error(
                "This virtual card does not have a PIN assigned.\n\n"
                "Assign a 6-8 digit numeric PIN using 'Set / Change PIN' before insertion."
            )
            return False

        if not meta.get("certificates"):
            self._error("This profile has no readable certificate.")
            return False

        try:
            card_type = meta.get("card_type", "piv").lower()
            card_cls = CacCard if card_type == "cac" else PivCard
            card = card_cls(pdir, meta, ask_secret=self._ask_secret)
            self.log(f"Reader {slot + 1}: software card type {card_type.upper()}")
            self.log(f"Reader {slot + 1}: private key {card._private_key_status()}")

            # vpcd maps the two exposed readers to their fixed TCP endpoints.
            port = VPCD_PORTS[slot]
            backend = VpcdTransport(
                card,
                [port],
                logger=lambda msg, s=slot: self.log(f"R{s + 1}: {msg}"),
                stopped_callback=lambda s=slot: self.software_backend_stopped(s),
            )
            self.software_backends[slot] = backend
            if slot == 0:
                self.software_backend = backend  # compatibility alias
            backend.start()

            time.sleep(0.30)
            if backend.last_error and not backend.running:
                err = backend.last_error
                self.software_backends[slot] = None
                if slot == 0:
                    self.software_backend = None
                self._error(f"Could not insert software card into Reader {slot + 1}:\n{err}")
                return False

            self._save_dual_state()
            self.log(
                f"Inserted {card_type.upper()} software card into Reader {slot + 1} "
                f"(port {port}): {meta.get('name')}"
            )
            self.update_ui()
        except Exception as exc:
            self.software_backends[slot] = None
            if slot == 0:
                self.software_backend = None
            self._error(f"Could not create software smartcard for Reader {slot + 1}:\n{exc}")

        return False

    def software_backend_stopped(self, slot=0):
        slot = int(slot)
        backend = self.software_backends.get(slot)
        if backend and not backend.running:
            self.software_backends[slot] = None
            if slot == 0:
                self.software_backend = None
            self._save_dual_state()
            self.update_ui()
        return False

    def _insert_proxy(self, pdir, meta):
        idx = meta.get("source_reader_index")
        cmd = ["vicc", "--type=relay"]
        help_rc, help_text = run_cmd(["vicc", "--help"], timeout=5)

        if idx is not None:
            if "--reader" in help_text:
                cmd += ["--reader", str(idx)]
            elif re.search(r"(^|\s)-r([,\s]|$)", help_text):
                cmd += ["-r", str(idx)]

        try:
            log_handle = open(VICC_LOG, "ab", buffering=0)
            self.vicc_process = subprocess.Popen(
                cmd,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            time.sleep(0.35)
            if self.vicc_process.poll() is not None:
                self.vicc_process = None
                self._error(f"Relay backend exited immediately. See:\n{VICC_LOG}")
                return False

            self._save_dual_state()
            self.log("Inserted physical-card proxy into Reader 1: " + " ".join(cmd))
            self.update_ui()
        except Exception as exc:
            self.vicc_process = None
            self._error(f"Could not start proxy:\n{exc}")
        return False

    def remove_card(self, *args, slot=0):
        slot = int(slot)
        backend = self.software_backends.get(slot)
        if backend:
            self.software_backends[slot] = None
            if slot == 0:
                self.software_backend = None
            backend.stop()
            self.log(f"Software virtual card removed from Reader {slot + 1}.")

        if slot == 0 and self.vicc_process is not None:
            try:
                os.killpg(os.getpgid(self.vicc_process.pid), signal.SIGTERM)
                try:
                    self.vicc_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(self.vicc_process.pid), signal.SIGKILL)
            except Exception as exc:
                self.log(f"Relay stop warning: {exc}")
            self.vicc_process = None
            self.log("Proxy virtual card removed from Reader 1.")

        self._save_dual_state()
        self.update_ui()
        return False

    def remove_all_cards(self):
        self.remove_card(slot=0)
        self.remove_card(slot=1)
        return False

    def toggle_card(self, *args, slot=0):
        return self.remove_card(slot=slot) if self.is_inserted(slot) else self.insert_card(slot=slot)

    def cycle_profile(self, delta):
        profiles = self.profile_dirs()
        if not profiles:
            return False
        ids = [m.get("id") for _, m in profiles]
        current = self.config.get("active_card")
        try:
            idx = ids.index(current)
        except ValueError:
            idx = 0
        self.config["active_card"] = ids[(idx + delta) % len(ids)]
        save_json(CONFIG_FILE, self.config)
        self.refresh_profiles()
        self.update_ui()
        return False

    def next_card(self):
        return self.cycle_profile(1)

    def previous_card(self):
        return self.cycle_profile(-1)

    def delete_profile(self, *_):
        d, meta = self.active_profile()
        if not d:
            return
        pid = meta.get("id")
        for slot in (0, 1):
            _pd, assigned = self.reader_profile(slot)
            if assigned and assigned.get("id") == pid and self.is_inserted(slot):
                self._error(f"Remove this profile from Reader {slot + 1} before deleting it.")
                return

        md = Gtk.MessageDialog(
            parent=self.window,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=f"Delete profile '{meta.get('name', d.name)}'?",
        )
        resp = md.run()
        md.destroy()
        if resp == Gtk.ResponseType.OK:
            shutil.rmtree(d)
            self.config["active_card"] = None
            for slot in ("0", "1"):
                if self.config.get("reader_profiles", {}).get(slot) == meta.get("id"):
                    self.config["reader_profiles"][slot] = None
            save_json(CONFIG_FILE, self.config)
            self.refresh_profiles()
            self.update_ui()

    # -------------------------------------------------------------- status

    def update_ui(self):
        d, meta = self.active_profile()
        name = meta.get("name") if meta else "No profile"

        reader_bits = []
        for slot in (0, 1):
            _pd, rm = self.reader_profile(slot)
            rname = rm.get("name") if rm else "No profile"
            state = "INSERTED" if self.is_inserted(slot) else "REMOVED"
            reader_bits.append(f"R{slot + 1}: {rname} [{state}]")
            if hasattr(self, "reader_state_labels"):
                if self.is_inserted(slot):
                    self.reader_state_labels[slot].set_markup(
                        '<span foreground="green"><b>INSERTED</b></span>'
                    )
                else:
                    self.reader_state_labels[slot].set_markup(
                        '<span foreground="red"><b>REMOVED</b></span>'
                    )

            if hasattr(self, "reader_action_buttons"):
                assigned = rm is not None
                buttons = self.reader_action_buttons.get(slot, {})
                if buttons:
                    buttons["insert"].set_sensitive(assigned and not self.is_inserted(slot))
                    buttons["remove"].set_sensitive(self.is_inserted(slot))
                    # Credential/personality editing is intentionally disabled
                    # while this assigned profile is live in either reader.
                    profile_busy = bool(
                        rm and self._profile_inserted_slots(rm.get("id"))
                    )
                    buttons["pin"].set_sensitive(assigned and not profile_busy)
                    buttons["card_type"].set_sensitive(assigned and not profile_busy)
                    buttons["password"].set_sensitive(
                        assigned and bool(rm.get("pkcs12")) and not profile_busy
                    )

        reader_state = (
            f"{len(self.vpcd_readers)} Virtual PCD reader(s)"
            if self.vpcd_readers else
            "Virtual PCD MISSING"
        )

        self.status_label.set_markup(
            f"<b>{GLib.markup_escape_text(reader_bits[0])}</b>    "
            f"<b>{GLib.markup_escape_text(reader_bits[1])}</b>    "
            f"<b>pcscd:</b> {GLib.markup_escape_text(reader_state)}"
        )

        icon = find_tray_icon()
        if icon:
            self.tray.set_from_file(str(icon))

        inserted_count = sum(1 for s in (0, 1) if self.is_inserted(s))
        self.tray.set_tooltip_text(
            f"{APP_NAME}: {inserted_count}/2 virtual reader(s) populated"
        )
        self.update_profile_details()
        self.update_pcsc_label()

    def health_check(self):
        if self.vicc_process is not None and self.vicc_process.poll() is not None:
            self.log(f"vicc relay stopped (exit {self.vicc_process.returncode}).")
            self.vicc_process = None
            self._save_dual_state()

        # A fresh client tells us whether the PC/SC service is actually alive.
        # Only call pyscard in this process after the fresh probe succeeds.
        names, _detail = self._fresh_virtual_reader_names()
        if names:
            self.refresh_readers()
        else:
            self.vpcd_readers = []
            self.physical_readers = []
            self._rebuild_reader_detail_tabs()

        self.update_ui()
        return True

    # ---------------------------------------------------------- diagnostics

    def diag_pcsc(self, *_):
        self.refresh_readers()
        lines = ["PC/SC readers:"]
        try:
            from smartcard.System import readers
            for i, r in enumerate(readers()):
                lines.append(f"  {i}: {r}")
        except Exception as exc:
            lines.append(f"  ERROR: {exc}")
        self.log("\n".join(lines))

    def diag_opensc(self, *_):
        rc, out = run_cmd(["opensc-tool", "--list-readers"], timeout=10)
        self.log(out.strip())

    def diag_vicc(self, *_):
        rc, out = run_cmd(["vicc", "--help"], timeout=10)
        self.log(out.strip())

    def diag_software_card(self, *_):
        if not self.is_inserted():
            self._info(
                "Insert a software card first, then run:\n\n"
                "pcsc_scan\n"
                "opensc-tool --list-readers\n"
                "opensc-tool --reader 0 --atr\n\n"
                "The Diagnostics log will also show every APDU sent to the software card."
            )
            return
        populated = [str(s + 1) for s in (0, 1) if self.is_inserted(s)]
        self.log("Software-card diagnostics: populated reader(s): " + ", ".join(populated))

    # --------------------------------------------------------------- tray

    def show_manager(self):
        self.refresh_profiles()
        self.refresh_readers()
        self.update_ui()
        self.window.show_all()
        self.window.present()
        return False

    def on_window_delete(self, *_):
        self.window.hide()
        return True

    def _popup_tray_menu(self, menu, icon, button, activate_time):
        """
        Prefer anchoring the menu to the actual StatusIcon geometry on X11.
        Gtk.StatusIcon.position_menu is retained as a fallback because some
        window managers/tray implementations do not expose icon geometry.
        """
        try:
            ok, screen, area, orientation = icon.get_geometry()
            if ok and screen is not None and area is not None:
                root = screen.get_root_window()
                if root is not None and hasattr(menu, "popup_at_rect"):
                    # Anchor menu immediately above the tray icon.
                    from gi.repository import Gdk
                    menu.popup_at_rect(
                        root,
                        area,
                        Gdk.Gravity.NORTH_WEST,
                        Gdk.Gravity.SOUTH_WEST,
                        None,
                    )
                    return
        except Exception as exc:
            self.log(f"Tray geometry positioning fallback: {exc}")

        # Standard GTK fallback. On some IGEL WM/tray combinations the WM may
        # still choose the final position.
        menu.popup(
            None, None, Gtk.StatusIcon.position_menu,
            icon, button, activate_time
        )

    def on_tray_menu(self, icon, button, activate_time):
        menu = Gtk.Menu()

        pcsc = Gtk.MenuItem(
            label=(
                f"PC/SC: {len(self.vpcd_readers)} Virtual PCD reader(s)"
                if self.vpcd_readers else
                "PC/SC: Virtual PCD missing"
            )
        )
        pcsc.set_sensitive(False)
        menu.append(pcsc)
        menu.append(Gtk.SeparatorMenuItem())

        profiles = self.profile_dirs()
        for slot in (0, 1):
            _pd, assigned = self.reader_profile(slot)
            state = "inserted" if self.is_inserted(slot) else "empty"
            label = assigned.get("name") if assigned else "No profile"
            parent = Gtk.MenuItem(label=f"Reader {slot + 1}: {label} ({state})")
            sub = Gtk.Menu()

            phead = Gtk.MenuItem(label="Assign profile")
            psub = Gtk.Menu()
            group = None
            assigned_id = assigned.get("id") if assigned else None
            for d, meta in profiles:
                x = Gtk.RadioMenuItem.new_with_label(
                    group, f"{meta.get('name', d.name)} [{meta.get('card_type', 'piv').upper()}]"
                )
                group = x.get_group()
                x.set_active(meta.get("id") == assigned_id)
                x.connect("activate", self.tray_assign_reader_profile, slot, meta.get("id"))
                psub.append(x)
            if not profiles:
                x = Gtk.MenuItem(label="No profiles configured")
                x.set_sensitive(False)
                psub.append(x)
            phead.set_submenu(psub)
            sub.append(phead)
            sub.append(Gtk.SeparatorMenuItem())

            ins = Gtk.MenuItem(label="Insert")
            ins.set_sensitive(not self.is_inserted(slot))
            ins.connect("activate", lambda _x, s=slot: self.insert_card(slot=s))
            sub.append(ins)
            rem = Gtk.MenuItem(label="Remove")
            rem.set_sensitive(self.is_inserted(slot))
            rem.connect("activate", lambda _x, s=slot: self.remove_card(slot=s))
            sub.append(rem)
            parent.set_submenu(sub)
            menu.append(parent)

        menu.append(Gtk.SeparatorMenuItem())
        x = Gtk.MenuItem(label="Open manager   Ctrl+Shift+F12")
        x.connect("activate", lambda *_: self.show_manager())
        menu.append(x)
        x = Gtk.MenuItem(label="Quit")
        x.connect("activate", self.quit)
        menu.append(x)

        menu.show_all()
        self._popup_tray_menu(menu, icon, button, activate_time)

    def tray_assign_reader_profile(self, item, slot, pid):
        if item.get_active() and pid:
            self.config.setdefault("reader_profiles", {"0": None, "1": None})[str(slot)] = pid
            save_json(CONFIG_FILE, self.config)
            self.refresh_profiles()
            self.update_ui()

    def tray_select_profile(self, item, pid):
        if item.get_active() and pid:
            self.config["active_card"] = pid
            save_json(CONFIG_FILE, self.config)
            self.refresh_profiles()
            self.update_ui()

    # --------------------------------------------------------------- dialogs

    def _ask_secret(self, title, prompt):
        d = Gtk.Dialog(title=title, parent=self.window)
        d.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK,
        )
        box = d.get_content_area()
        box.pack_start(Gtk.Label(label=prompt), False, False, 4)
        e = Gtk.Entry()
        e.set_visibility(False)
        e.set_invisible_char("•")
        box.pack_start(e, False, False, 4)
        d.show_all()
        if d.run() == Gtk.ResponseType.OK:
            value = e.get_text()
            d.destroy()
            return value
        d.destroy()
        return None

    def _ask_text(self, title, prompt, initial=""):
        d = Gtk.Dialog(title=title, parent=self.window)
        d.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK,
        )
        box = d.get_content_area()
        box.pack_start(Gtk.Label(label=prompt), False, False, 4)
        e = Gtk.Entry()
        e.set_text(initial)
        box.pack_start(e, False, False, 4)
        d.show_all()
        if d.run() == Gtk.ResponseType.OK:
            value = e.get_text().strip()
            d.destroy()
            return value
        d.destroy()
        return None

    def _info(self, text):
        d = Gtk.MessageDialog(
            parent=self.window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=text,
        )
        d.run()
        d.destroy()

    def _error(self, text):
        d = Gtk.MessageDialog(
            parent=self.window,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=text,
        )
        d.run()
        d.destroy()

    # --------------------------------------------------------------- logging

    def _append_log_ui(self, line):
        """
        Append a diagnostic line from the GTK main loop only.

        vpcd/APDU traffic is handled by a worker thread. GTK widgets are not
        thread-safe, and writing directly to Gtk.TextView from that worker can
        abort GTK with gtk_text_view_validate_onscreen assertions.
        """
        try:
            buf = self.log_view.get_buffer()
            buf.insert(buf.get_end_iter(), line)

            # Keep diagnostics bounded so a long authentication session does
            # not grow the TextBuffer forever.
            line_count = buf.get_line_count()
            max_lines = 4000
            if line_count > max_lines:
                trim_to = buf.get_iter_at_line(line_count - max_lines)
                start = buf.get_start_iter()
                buf.delete(start, trim_to)

            mark = buf.create_mark(None, buf.get_end_iter(), False)
            self.log_view.scroll_to_mark(mark, 0.0, False, 0.0, 1.0)
            buf.delete_mark(mark)
        except Exception as exc:
            print(f"[IGELVSC UI log error] {exc}", file=sys.stderr, flush=True)
        return False

    def log(self, msg):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}\n"
        print(line, end="", flush=True)

        # Never touch GTK widgets from worker threads. Scheduling everything
        # through idle_add is cheap enough for diagnostics and also keeps the
        # behavior consistent for callers already running on the GTK thread.
        try:
            GLib.idle_add(self._append_log_ui, line)
        except Exception as exc:
            print(f"[IGELVSC log scheduling error] {exc}", file=sys.stderr, flush=True)
        return False

    # --------------------------------------------------------------- quit

    def quit(self, *_):
        # Snapshot the desired insertion state before stopping the backends.
        # remove_card() necessarily makes the runtime state false, so write the
        # remembered state back after cleanup for the next launch.
        remembered = {}
        for slot in (0, 1):
            _pdir, meta = self.reader_profile(slot)
            remembered[str(slot)] = {
                "inserted": self.is_inserted(slot),
                "profile_id": meta.get("id") if meta else None,
                "vpcd_port": VPCD_PORTS[slot],
            }

        self._quitting = True
        self.remove_all_cards()
        self.state = {"readers": remembered}
        save_json(STATE_FILE, self.state)

        self.hotkeys.stop()

        # Deliberately leave pcscd running for now. PC/SC lifecycle restoration
        # remains a separate service-management improvement.
        Gtk.main_quit()

    def run(self):
        # Tray-first behavior: if at least one virtual-card profile exists,
        # start quietly in the notification area. If there are no profiles,
        # show the manager so the user can import the first certificate.
        if self.profile_dirs():
            self.window.hide()
        else:
            self.window.show_all()
            self.window.present()
        Gtk.main()


def main():
    app = IgelVSC()
    app.run()


if __name__ == "__main__":
    main()
