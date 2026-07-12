# iaiops — Industrial-AIOps (governed, read-first OT diagnostics)

[Industrial-AIOps (`iaiops`)](https://github.com/industrial-aiops/industrial-aiops)
is a **vendor-neutral, read-first** operational-technology (OT) data tap and
cross-protocol troubleshooting brain, exposed to AI agents as **governed MCP
tools**. It reads ~14 field protocols (OPC-UA, Modbus, S7comm, Mitsubishi MC,
Omron FINS, MTConnect, MQTT/Sparkplug B, EtherNet/IP, EtherCAT, PROFINET,
SECS/GEM, HART-IP, BACnet/IP, IO-Link) plus per-industry editions (factory,
process, fab, building, water, warehouse, clinical, renewables). MIT-licensed.

This is a **container-launcher recipe**: it runs the published, hardened iaiops
**OCI image** on the endpoint via **Podman** — there is no native binary to
package. Discussed and placed here per
[issue #518](https://github.com/IGEL-Community/IGEL-OS-APP-RECIPES/issues/518).

## How it works

- **Nothing is copied into the root filesystem.** The app runs entirely from its
  OCI image; the only thing laid down is the systemd unit
  (`/etc/systemd/system/iaiops.service`) that links it in.
- **All writable state lives in `/services_rw/iaiops`** (declared persistent in
  `igel/dirs.json`, sized via `app.json` `rw_partition`). It is mounted into the
  container as `IAIOPS_HOME=/state`, so the audit / policy / undo store and the
  site `config.yaml` persist across reboots.
- The unit is **read-first and hardened**: `--read-only` rootfs, `--cap-drop=ALL`,
  `--security-opt=no-new-privileges`. The MCP endpoint binds to **localhost**.

## Site configuration

Drop an optional `iaiops.env` in `/services_rw/iaiops/` to pick your edition and
lock down the endpoint (overrides the unit defaults):

```sh
# /services_rw/iaiops/iaiops.env
IAIOPS_IMAGE=ghcr.io/industrial-aiops/iaiops:0.12.0-building
IAIOPS_MCP=building
IAIOPS_MCP_TRANSPORT=sse
IAIOPS_ALLOWLIST_ACCOUNTS=ops-agent
IAIOPS_ALLOWLIST_IPS=10.0.0.0/24
```

Protocol targets (endpoints/credentials) go in `/services_rw/iaiops/config.yaml`
(i.e. `IAIOPS_HOME=/state`), not baked into the image.

## Security posture

Read-first by design: every tool runs through iaiops' built-in **governance
harness** (audit log, token/runaway budget, graduated risk tiers, undo). The few
write/command tools are off by default (dry-run + double-confirm + MOC approval).
Expose the MCP endpoint **only** behind the account/IP allowlist above.

## Status

Community recipe, not yet validated on a specific IGEL OS 12 endpoint — feedback
welcome. Source and full tool reference:
<https://github.com/industrial-aiops/industrial-aiops>.
