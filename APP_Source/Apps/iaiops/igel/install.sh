#!/bin/bash
# Enable the systemd unit that launches the iaiops container via Podman.
# Nothing is copied into the root filesystem: the app lives in /services/iaiops,
# its writable state in /services_rw/iaiops, and this unit is the only link in.
enable_system_service iaiops.service
