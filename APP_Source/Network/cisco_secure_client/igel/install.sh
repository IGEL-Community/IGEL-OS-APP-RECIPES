#!/bin/bash
MOUNT_OPT="${MOUNTPOINT}/opt"
CACHE_OPT="${CACHEPATH}/opt"
MOUNT_CISCO="${MOUNT_OPT}/cisco"
CACHE_CISCO="${CACHE_OPT}/cisco"
MOUNT_CA="${MOUNT_OPT}/.cisco/certificates/ca"
CACHE_CA="${CACHE_OPT}/.cisco/certificates/ca"
MOUNT_SECURECLIENT="${MOUNT_CISCO}/secureclient"
RW_PART="/services_rw/cisco_secure_client"
RW_SECURECLIENT="${RW_PART}/opt/cisco/secureclient"
USERHOME_CISCO="/userhome/.cisco"


if ! [ -f "${CACHE_CISCO}" ]; then
  mkdir -p "${CACHE_CISCO}"
fi
ln -s "${MOUNT_CISCO}/secureclient" "${CACHE_CISCO}/"

if ! [ -f "${CACHE_CA}" ]; then
  mkdir -p "${CACHE_CA}"
fi
ln -s "${MOUNT_CA}/"* "${CACHE_CA}/"

ln -s "${MOUNTPOINT}/RequestXMLSchema.xsd" "${CACHEPATH}/"

if ! [ -f "${RW_SECURECLIENT}" ]; then
  mkdir -p "${RW_SECURECLIENT}"
fi

enable_system_service igel-cisco-secure-client-watcher.service
enable_system_service igel-cisco-secure-client-config.service
enable_system_service igel-vpnagentd.service