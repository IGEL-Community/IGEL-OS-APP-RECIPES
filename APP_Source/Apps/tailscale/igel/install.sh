#!/bin/bash

# Enable tailscaled system service
enable_system_service tailscaled.service

# Create necessary directories for tailscale state
mkdir -p /services_rw/tailscale/var/lib/tailscale
ln -sf /services_rw/tailscale/var/lib/tailscale /var/lib/tailscale

# Ensure tailscale binary is in PATH
ln -sf /services/tailscale/usr/bin/tailscale /usr/bin/tailscale
ln -sf /services/tailscale/usr/sbin/tailscaled /usr/sbin/tailscaled
