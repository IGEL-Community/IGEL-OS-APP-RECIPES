# Tailscale IGEL OS 12 Smoke Test Instructions

## Prerequisites
1. IGEL OS 12 VM or physical device
2. Built Tailscale package files (.inf and .tar.bz2)
3. Valid Tailscale auth key for testing

## Installation Steps

### 1. Transfer Package Files
Transfer the generated files to your IGEL OS 12 device:
```bash
# On your build machine, locate the built packages:
ls -la APP_Packages/tailscale_*.inf
ls -la APP_Packages/tailscale_*.tar.bz2

# Transfer to IGEL device (replace <igel-ip> with actual IP):
scp APP_Packages/tailscale_*.inf user@<igel-ip>:/tmp/
scp APP_Packages/tailscale_*.tar.bz2 user@<igel-ip>:/tmp/
```

### 2. Install on IGEL OS 12
On the IGEL device:
```bash
# Navigate to temporary directory
cd /tmp

# Install the package using IGEL's package manager
sudo /sbin/igel-app-installer install tailscale_*.inf

# Verify installation
ls -la /userhome/.config/sessions/tailscale*
ls -la /lib/systemd/system/tailscaled.service
```

### 3. Start Tailscale Service
```bash
# Enable and start the tailscaled service
sudo systemctl enable tailscaled
sudo systemctl start tailscaled

# Check service status
sudo systemctl status tailscaled
```

### 4. Authenticate with Tailscale
```bash
# Run tailscale up with your auth key
# Replace <your-auth-key> with an actual auth key from https://login.tailscale.com/admin/settings/keys
sudo tailscale up --authkey=<your-auth-key>

# Alternatively, for interactive authentication:
sudo tailscale up
```

### 5. Verify Connectivity
```bash
# Check Tailscale status
tailscale status

# Test connectivity to another node (if available)
tailscale ping <another-node-name>

# Check IP addresses
tailscale ip -4
tailscale ip -6

# Verify network interfaces
ip addr show tailscale0
```

## Expected Results

1. **Service Status**: `tailscaled.service` should show as "active (running)"
2. **Authentication**: Device should appear in your Tailscale admin console
3. **Network Interface**: `tailscale0` interface should be present and have an IP
4. **Connectivity**: Should be able to ping other nodes in your tailnet

## Troubleshooting

### If service fails to start:
```bash
# Check logs
sudo journalctl -u tailscaled -f

# Check for permission issues
ls -la /var/lib/tailscale/
```

### If authentication fails:
```bash
# Try reauthenticating
sudo tailscale logout
sudo tailscale up --authkey=<new-auth-key>
```

### Check IGEL-specific paths:
```bash
# Verify RW partition mount (if configured)
mount | grep rw

# Check for proper file permissions
ls -la /usr/bin/tailscale*
```

## Cleanup (if needed)
```bash
# Stop and disable service
sudo systemctl stop tailscaled
sudo systemctl disable tailscaled

# Uninstall package
sudo /sbin/igel-app-installer uninstall tailscale
```

## Notes
- Ensure firewall rules allow Tailscale traffic (UDP 41641)
- The package should persist across IGEL device reboots
- Check IGEL's network settings don't conflict with Tailscale routes
