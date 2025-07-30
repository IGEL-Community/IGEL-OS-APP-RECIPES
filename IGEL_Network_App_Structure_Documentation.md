# IGEL Network App Recipe Structure Documentation

Based on analysis of F5 VPN, Tailscale, OpenConnect, and Cloudflare WARP apps from IGEL-Community/IGEL-OS-APP-RECIPES

## 1. File Tree Layout

```
APP_Source/Network/<app_name>/
├── app.json                    # Main app metadata
├── README.md                   # App documentation
├── data/                       # App resources
│   ├── app.png                 # App icon (color)
│   ├── monochrome.png          # App icon (monochrome)
│   ├── descriptions/
│   │   └── en                  # English description
│   ├── changelogs/
│   │   └── en                  # English changelog
│   └── config/
│       └── config.param        # App configuration parameters
├── igel/                       # IGEL-specific files
│   ├── dirs.json               # Directory structure definition (optional)
│   ├── install.json            # Installation file mapping
│   ├── thirdparty.json         # Third-party package definitions (OR debian.json)
│   ├── debian.json             # (alternative) Debian package definitions
│   ├── install.sh              # Post-installation script (optional)
│   └── pre_package_commands.sh # (optional) Pre-packaging commands
└── input/                      # Files to be installed
    └── all/
        ├── config/
        │   └── sessions/       # Session scripts
        │       └── <app_name>0 # Default session script
        └── lib/systemd/system/ # OR etc/systemd/system/
            └── <service>.service # Systemd unit files
```

## 2. JSON Schema Usage

### 2.1 app.json
```json
{
  "categories": ["Network"],        // or ["Miscellaneous"]
  "icons": {
    "app": "app.png",
    "monochrome": "monochrome.png"
  },
  "name": "tailscale",              // App identifier
  "author": "The IGEL community",
  "vendor": "Tailscale Inc.",       // Original vendor
  "rw_partition": {
    "size": "small",
    "flags": ["compressed"]
  },
  "release": "",
  "summary": {
    "en": "Tailscale VPN (Community)"
  },
  "version": "1.78.1+1"            // <upstream_version>+<recipe_version>
}
```

### 2.2 dirs.json (optional)
```json
[
  {
    "path": "/var/lib/tailscale",    // Directory path
    "owner": "0:0",                  // Numeric UID:GID (0:0 = root:root)
    "permissions": "755",            // Octal permissions
    "persistent": true               // Persist across reboots
  },
  {
    "path": "/userhome/.F5Networks",
    "persistent": true,
    "owner": "777:100"               // 777:100 = user:users
  }
]
```

**Key Schema Points:**
- `owner`: Must use numeric UID:GID format (not usernames)
  - 0:0 = root:root
  - 777:100 = user:users
- `permissions`: Octal format as string (e.g., "755", "700")
- `persistent`: Boolean, marks directories to persist across reboots
- **Note**: dirs.json is optional. Some apps rely on systemd StateDirectory/RuntimeDirectory instead

### 2.3 install.json
```json
[
  {
    "source": "usr/bin/tailscale",         // Source path (relative)
    "destination": "/usr/bin/tailscale"    // Destination path (absolute)
  },
  {
    "source": "usr/sbin/tailscaled",
    "destination": "/usr/sbin/tailscaled"
  },
  {
    "source": ".*",                        // Regex pattern for all files
    "excludes": [""]                       // Exclusion patterns
  }
]
```

### 2.4 thirdparty.json
```json
[
  {
    "url": "tailscale_1.78.1_amd64.deb",   // Relative or absolute URL
    "licenses": [
      {
        "name": "BSD-3-Clause"             // SPDX license identifier
      }
    ]
  },
  {
    "url": "file:///tmp/linux_f5vpn.x86_64.deb",  // Local file URL
    "licenses": [
      {
        "name": "MPL-2.0"
      }
    ]
  }
]
```

### 2.5 debian.json (alternative to thirdparty.json)
```json
[
  {
    "package": "openconnect",
    "licenses": [
      {
          "name": "LGPL-2.1-or-later"
      }
    ]    
  },
  {
    "package": "libopenconnect5",
    "licenses": [
      {
          "name": "LGPL-2.1-or-later"
      }
    ]    
  }
]
```

**Key Differences:**
- `thirdparty.json`: Used for downloading .deb files from URLs or local files
- `debian.json`: Used for installing packages directly from Debian repositories

## 3. Systemd Unit Placement

### 3.1 File Locations
- **System services**: `input/all/lib/systemd/system/` (preferred)
- **Alternative**: `input/all/etc/systemd/system/`

### 3.2 Service File Example (tailscaled.service)
```ini
[Unit]
Description=Tailscale node agent
Documentation=https://tailscale.com/kb/
After=network-pre.target
Wants=network-pre.target

[Service]
EnvironmentFile=/etc/default/tailscaled
ExecStartPre=/usr/sbin/tailscaled --cleanup
ExecStart=/usr/sbin/tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/run/tailscale/tailscaled.sock --port=${PORT} $FLAGS
ExecStopPost=/usr/sbin/tailscaled --cleanup
Restart=on-failure
RuntimeDirectory=tailscale
RuntimeDirectoryMode=0755
StateDirectory=tailscale
StateDirectoryMode=0700
CacheDirectory=tailscale
CacheDirectoryMode=0750
Type=notify

[Install]
WantedBy=multi-user.target
```

### 3.3 Service Enablement
Services are enabled via `igel/install.sh` (optional):
```bash
#!/bin/bash
# For root services:
enable_system_service tailscaled.service

# For user services:
enable_system_user_service warp-taskbar.service
```

**Alternative**: Some apps use a separate install script:
```bash
# install/install.sh
#!/bin/bash
enable_system_service warp-svc.service
enable_system_user_service warp-taskbar.service
```

## 4. Session Scripts

Located at: `input/all/config/sessions/<app_name>0`

Example structure:
```bash
#!/bin/bash
# Environment setup
export LD_LIBRARY_PATH=/services/<app_name>/opt/<vendor>/lib

# Service check and startup
if ! systemctl is-active --quiet <service_name>; then
    echo "Starting <service_name> service..."
    sudo systemctl start <service_name>
    sleep 2
fi

# Main application launch or status check
<application_command>
```

## 5. Key Patterns for Network Apps

1. **Persistent Storage**: Network apps typically need persistent directories for:
   - Configuration files
   - Authentication/state data
   - VPN credentials
   - Can be defined in dirs.json OR via systemd StateDirectory

2. **System Services**: Most Network apps run as system services:
   - Use systemd unit files
   - Enable via `enable_system_service` in install.sh
   - Often require root privileges (owner "0:0")
   - May include both system and user services

3. **Directory Permissions**:
   - State directories: Usually mode 700 or 755
   - Config directories: Mode 755
   - User directories: Owner "777:100" for user access
   - Runtime directories: Often handled by systemd

4. **Package Management**:
   - Two approaches:
     - `thirdparty.json`: Download .deb files from URLs
     - `debian.json`: Install from Debian repositories
   - Always specify licenses (SPDX identifiers)

5. **Service Capabilities**: Network services often need special permissions:
   ```ini
   CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE CAP_NET_RAW
   AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE CAP_NET_RAW
   ```

6. **Installation Flexibility**:
   - Simple apps: Just use install.json with regex patterns
   - Complex apps: Use specific file mappings in install.json
   - Service enablement: Can be in igel/install.sh or install/install.sh

This structure serves as the template for creating IGEL Network app recipes.
