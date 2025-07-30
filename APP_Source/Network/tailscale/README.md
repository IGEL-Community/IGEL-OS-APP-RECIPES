# Tailscale for IGEL OS

This recipe creates a Tailscale VPN package for IGEL OS 12.

## Description

Tailscale is a zero-configuration VPN that creates a secure network between your devices. It uses WireGuard for encrypted point-to-point connections and works seamlessly behind firewalls and NATs.

## Requirements

- IGEL OS 12.3.0 or later
- For OS 12.5.0+: Compatibility layer for 12.0.x apps
- Valid Tailscale auth key or interactive authentication

## Configuration

The package includes:
- `tailscale` CLI tool
- `tailscaled` daemon
- Systemd service configuration
- Persistent storage for authentication state

## Usage

1. Deploy the application via UMS
2. Start a Tailscale session from the desktop
3. Authenticate using one of these methods:
   - Interactive: `sudo tailscale up`
   - Auth key: `sudo tailscale up --authkey=YOUR_KEY`

## Files

- Binary location: `/services/tailscale/usr/bin/tailscale`
- Daemon location: `/services/tailscale/usr/sbin/tailscaled`
- Persistent data: `/services_rw/tailscale/var/lib/tailscale`

## Version

Current version: 1.78.1+1 (Based on Tailscale 1.78.1)