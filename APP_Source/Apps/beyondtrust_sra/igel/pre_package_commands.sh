#!/bin/bash
#
# pre_package_command.sh
# BeyondTrust SRA — verify .bin placement
#

echo "=== BeyondTrust SRA Pre-Package ==="

# The builder already extracted beyondtrust-sra.tar.bz2 via third_party.json
# Find where the .bin ended up
SRA_BIN=$(find . -name "sra-pin-linux*.bin" 2>/dev/null | head -1)

if [ -z "${SRA_BIN}" ]; then
  SRA_BIN=$(find /thirdparty -name "sra-pin-linux*.bin" 2>/dev/null | head -1)
fi

if [ -n "${SRA_BIN}" ]; then
  echo "Found SRA binary: ${SRA_BIN}"
  chmod +x "${SRA_BIN}"
else
  echo "WARNING: Could not locate sra-pin-linux*.bin"
  echo "=== Debug: current directory ==="
  pwd && ls -laR
  echo "=== Debug: /thirdparty ==="
  ls -laR /thirdparty/ 2>/dev/null
fi

# Verify static files made it into the build
if [ -f "input/all/etc/beyondtrust/beyondtrust-init.sh" ] 2>/dev/null; then
  echo "Init script: found in input"
elif [ -f "etc/beyondtrust/beyondtrust-init.sh" ] 2>/dev/null; then
  echo "Init script: found in build root"
else
  echo "WARNING: beyondtrust-init.sh not found (may already be copied)"
fi

echo "pre_package_command.sh completed"