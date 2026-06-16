#!/bin/bash
# Disable the BeyondTrust SRA Jump Client
disable_system_service beyondtrust-sra.service

# Stop and remove any running SRA instance
SRA_INST_DIR=$(ls -d /opt/beyondtrust/sra-pin-* 2>/dev/null | head -1)
if [ -n "${SRA_INST_DIR}" ]; then
  INST_NAME=$(basename "${SRA_INST_DIR}")
  systemctl stop "${INST_NAME}.service" 2>/dev/null
  systemctl disable "${INST_NAME}.service" 2>/dev/null
  rm -f "/etc/systemd/system/${INST_NAME}.service"

  if [ -x "${SRA_INST_DIR}/uninstall" ]; then
    "${SRA_INST_DIR}/uninstall"
  else
    rm -rf "${SRA_INST_DIR}"
  fi

  systemctl daemon-reload
fi

rm -rf /opt/beyondtrust 2>/dev/null