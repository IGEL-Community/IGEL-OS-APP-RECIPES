#!/bin/bash
#
# beyondtrust-init.sh
# BeyondTrust SRA Jump Client for IGEL OS 25.3.1 — Official Option 2

APP_PATH=/services/beyondtrust_sra
SRA_INSTALL_BASE=/opt/beyondtrust
SESSION_WRAPPER=${SRA_INSTALL_BASE}/session-wrapper.sh
IGEL_USER=user
LOGGER='logger -it beyondtrust_sra_'
$LOGGER "=== BeyondTrust SRA Jump Client Init (25.3.1) ==="

# Ensure directory exists BEFORE creating wrapper
mkdir -p "${SRA_INSTALL_BASE}"

# Create session-wrapper via heredoc (now guaranteed to succeed)
$LOGGER "Creating session-wrapper.sh"
cat > "${SESSION_WRAPPER}" << 'WRAPEOF'
#!/bin/bash
# BeyondTrust Session Wrapper for IGEL OS
export DISPLAY=:0
exec "$@"
WRAPEOF

chmod +x "${SESSION_WRAPPER}"
$LOGGER "session-wrapper ready at ${SESSION_WRAPPER}"

# ---------------------------------------------------------------
# 1. EXISTING installation
# ---------------------------------------------------------------
SRA_INST_DIR=$(ls -d "${SRA_INSTALL_BASE}"/sra-pin-* 2>/dev/null | head -1)
if [ -n "${SRA_INST_DIR}" ] && [ -d "${SRA_INST_DIR}" ]; then
  INST_NAME=$(basename "${SRA_INST_DIR}")
  $LOGGER "Existing installation: ${SRA_INST_DIR}"

  if [ -x "${SRA_INST_DIR}/init-script" ]; then
    "${SRA_INST_DIR}/init-script" start
    $LOGGER "Started via init-script"
  else
    systemctl start "${INST_NAME}.service" 2>/dev/null
    $LOGGER "Started via systemctl"
  fi

  sleep 3
  su - ${IGEL_USER} -c "DISPLAY=:0 xhost +SI:localuser:root" 2>/dev/null || true
  $LOGGER "X11 access granted"

  echo "Finished"
  $LOGGER "Finished (existing installation started)"
  exit 0
fi

# ---------------------------------------------------------------
# 2. FIRST BOOT ONLY — official 25.3.1 flags
# ---------------------------------------------------------------
$LOGGER "No existing installation — first boot"
SRA_BIN=$(ls "${APP_PATH}/" 2>/dev/null | grep -m1 -E '^sra-pin-linux.*\.bin$')
if [ -z "${SRA_BIN}" ]; then
  $LOGGER "ERROR: No sra-pin-linux*.bin found"
  exit 1
fi

$LOGGER "Running official 25.3.1 installer"
chmod +x "${APP_PATH}/${SRA_BIN}"
sh "${APP_PATH}/${SRA_BIN}" \
  --headless \
  --scope system \
  --session-wrapper "${SESSION_WRAPPER}" \
  --session-user "${IGEL_USER}"

# Poll for install directory
TIMEOUT=120
ELAPSED=0
while [ ${ELAPSED} -lt ${TIMEOUT} ]; do
  SRA_INST_DIR=$(ls -d "${SRA_INSTALL_BASE}"/sra-pin-* 2>/dev/null | head -1)
  if [ -n "${SRA_INST_DIR}" ]; then
    INST_NAME=$(basename "${SRA_INST_DIR}")
    $LOGGER "Installation detected"
    break
  fi
  sleep 5
  ELAPSED=$((ELAPSED + 5))
done

if [ -z "${SRA_INST_DIR}" ]; then
  $LOGGER "ERROR: Install not found"
  exit 1
fi

# Start service + xhost
systemctl start "${INST_NAME}.service" 2>/dev/null
sleep 3
su - ${IGEL_USER} -c "DISPLAY=:0 xhost +SI:localuser:root" 2>/dev/null || true
$LOGGER "X11 access granted"

echo "Finished"
$LOGGER "Finished (first boot — 25.3.1 complete)"
exit 0