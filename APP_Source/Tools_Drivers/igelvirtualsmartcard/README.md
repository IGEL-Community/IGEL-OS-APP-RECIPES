THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# IGEL Virtual Smartcard

- Based on [Virtual Smart Card](https://frankmorgner.github.io/vsmartcard/)

Virtual Smart Card emulates a smart card and makes it accessible through PC/SC. Currently the Virtual Smart Card supports the following types of smart cards:

- Generic ISO-7816 smart card including secure messaging
- German electronic identity card (nPA) with complete support for EAC (PACE, TA, CA)
- Electronic passport (ePass/MRTD) with support for BAC
- Cryptoflex smart card (incomplete)

[IGEL Virtual Smart Card app demo](https://youtu.be/plHqE6T7jBQ?si=Hl5_MS04tRZSb1tq)

## Main application: dynamic reader details

The lower details notebook now contains:

```text
Virtual Reader 1 profile
Virtual Reader 2 profile
Physical Reader 1 profile
Physical Reader 2 profile
...
```

The physical-reader pages are created and removed dynamically from the live
PC/SC reader list. They show the reader name, PC/SC index, current card state
and ATR when a card is inserted.

Full OpenSC/PKCS#15 inspection remains in the **Physical Cards** tab so that the
2-second health check does not repeatedly execute expensive middleware tools.

## Minimal utility

A second executable is included:

```text
igel_virtual_smartcard_minimal.py
```

It is intentionally separate from the full manager.

### Certificate location

It scans:

```text
/userhome/.config/igelvsc/*.pfx
```

The first PFX alphabetically is automatically selected and inserted into:

```text
Virtual PCD 00 00
```

If multiple PFX files exist, they can be switched from the tray menu.

### Card personality

PIV is the default, so simply run:

```bash
./igelvirtualsmartcard-minimal-launcher
```

or:

```bash
./igel_virtual_smartcard_minimal.py
```

Use CAC explicitly with:

```bash
./igel_virtual_smartcard_minimal.py --cac
```

There is no `--piv` option anymore; PIV is the default personality.

### Password storage

For password-protected PFX files, the utility prompts for the certificate
password when the PFX is first selected and offers:

```text
[x] Store certificate password encrypted
```

Disable password storage/use for the run with:

```bash
./igel_virtual_smartcard_minimal.py --piv --nopwdstore
```

Stored secrets use the same AES-GCM master-key concept as the full app.

### PIN

The first time a PFX is used, its virtual-card PIN is:

```text
000000
```

Use the tray menu:

```text
Change / reset PIN
```

to set a new 6-8 digit numeric PIN.

For a password-protected PFX, changing/resetting the PIN requires entering the
PFX certificate password and validating it against the PFX first. A stored
certificate password is deliberately *not* accepted silently for PIN reset.

### Shutdown

Quitting the minimal utility stops the card backend, which removes the card
from Virtual PCD 00 00. The Virtual PCD reader itself may remain available
through pcscd.

## Files

```text
igel_virtual_smartcard.py
igel_virtual_smartcard_minimal.py
igelvirtualsmartcard-launcher
igelvirtualsmartcard-minimal-launcher
```


## v0.4.4 minimal-utility fixes

- Fixed PFX password validation so a valid password is not reported as wrong
  merely because OpenSSL cannot decrypt a legacy certificate bag.
- Password validation now checks the PKCS#12/MAC first.
- OpenSSL PKCS#12 operations retry with `-legacy` when OpenSSL 3 reports an
  unsupported legacy algorithm.
- Non-password PKCS#12 errors are now shown as such instead of saying
  "Incorrect certificate password".
- The minimal tray utility now uses exactly the same IGEL Virtual Smartcard
  tray icon lookup as the full manager.
- PIV is the default; `--piv` has been removed. `--cac` is the only personality
  override.


## v0.4.5 reader-detail formatting

The reader profile tabs are reformatted into clear sections:

- Reader/state
- Profile
- Certificates
- Key material
- Smartcard backend
- Warnings

The text view now uses a monospace font and padding for easier scanning.

This also fixes the v0.4.3/v0.4.4 regression where literal `\\n` sequences
could appear in the Reader profile text instead of real line breaks.


## v0.4.6 native reader-detail scrolling

Reader profile text is no longer rewritten on every periodic health refresh.

Previously, `Gtk.TextBuffer.set_text()` was called every few seconds even when
the displayed profile had not changed. GTK consequently recalculated the
TextView layout and returned the scrollbar to the top.

v0.4.6 now:

- updates a reader-detail buffer only when its content actually changes;
- preserves the current vertical scroll offset across legitimate state changes;
- avoids rebuilding physical-reader detail tabs unless the physical reader set
  itself changes;
- preserves scrolling in physical-reader detail pages as their card state is
  refreshed.

Mouse-wheel, touchpad, scrollbar and keyboard scrolling can therefore behave as
normal native GTK scrolling and remain at the user's current position.


## v0.4.7 card-type dialog

The **Set virtual smartcard type** dialog has been redesigned:

- compact fixed-width dialog that stays within the main application window;
- radio-button selection instead of a drop-down list;
- one radio button per card personality currently implemented by the app;
- current built-in choices are **PIV-II** and **CAC**;
- the UI is registry-driven, so a future virtual-card backend can add another
  entry to `CARD_TYPE_REGISTRY` and it will automatically appear as another
  radio-button choice.

Only actual virtual-card personalities should be registered here. A generic
PKCS#11 middleware module by itself is not a new card personality unless there
is a corresponding emulation backend for it.


## v0.4.8 tray-first startup and session state

The full manager now starts tray-only when at least one certificate profile
already exists. If no profiles exist, the manager opens automatically so the
first certificate can be imported.

Reader insertion state is remembered on Quit. If Reader 1 and/or Reader 2 were
inserted at shutdown, the same profiles are automatically reinserted on the
next launch once Virtual PCD is ready.

Global hotkeys are now:

```text
Ctrl+Shift+F9   Toggle Reader 1
Ctrl+Shift+F10  Toggle Reader 2
Ctrl+Shift+F11  Next profile
Ctrl+Shift+F12  Open manager
```

This avoids Ctrl+Alt+Fn combinations used by Linux/IGEL for VT/console
switching.

Tray-menu positioning now first tries to anchor directly to the actual
`Gtk.StatusIcon` geometry on X11. If the IGEL window manager/tray does not
provide usable geometry, it falls back to GTK's standard StatusIcon menu
positioning.

## v0.4.8 minimal certificate store

The minimal utility now scans only:

```text
/userhome/.config/igelvsc/mini-utility-certstore/
```

At startup it uses the IGEL-supported:

```text
su -c "<command>" root
```

mechanism to normalize that directory and its files to owner `user:user` with
user read/write access.

The directory is polled at runtime. When files are added or changed, ownership
and access are normalized again before subsequent selection/use.


## v0.4.9 minimal utility ownership fix

IGEL OS has the login user `user`, but it does not necessarily have a matching
group named `user`. The minimal utility previously used:

```text
chown -R user:user ...
```

which fails on such systems with:

```text
chown: invalid group: 'user:user'
```

v0.4.9 now uses owner-only syntax:

```text
chown -R user ...
```

and applies restrictive permissions suitable for PFX/private-key material:

```text
directories: 0700
files:       0600
```

The same normalization is performed at startup and whenever the certificate
store changes at runtime.
