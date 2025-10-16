#!/bin/bash
set -e

INSTPREFIX=/services/cisco_secure_client/opt/cisco/secureclient
BINDIR=${INSTPREFIX}/bin

# generate default AnyConnect Local Policy file if it doesn't already exist
${BINDIR}/acinstallhelper -acpolgen bd=${BYPASS_DOWNLOADER:-false} \
                                    rswd=${RESTRICT_SCRIPT_WEBDEPLOY:-false} \
                                    rhwd=${RESTRICT_HELP_WEBDEPLOY:-false} \
                                    rrwd=${RESTRICT_RESOURCE_WEBDEPLOY:-false} \
                                    rlwd=${RESTRICT_LOCALIZATION_WEBDEPLOY:-false} \
                                    fm=${FIPS_MODE:-false} \
                                    rpc=${RESTRICT_PREFERENCE_CACHING:-false} \
                                    rtp=${RESTRICT_TUNNEL_PROTOCOLS:-false} \
                                    rwl=${RESTRICT_WEB_LAUNCH:-false} \
                                    sct=${STRICT_CERTIFICATE_TRUST:-false} \
                                    efn=${EXCLUDE_FIREFOX_NSS_CERT_STORE:-false} \
                                    upsu=${ALLOW_SOFTWARE_UPDATES_FROM_ANY_SERVER:-true} \
                                    upcu=${ALLOW_COMPLIANCE_MODULE_UPDATES_FROM_ANY_SERVER:-true} \
                                    upvp=${ALLOW_VPN_PROFILE_UPDATES_FROM_ANY_SERVER:-true} \
                                    upmv=${ALLOW_MGMT_VPN_PROFILE_UPDATES_FROM_ANY_SERVER:-true} \
                                    upip=${ALLOW_ISE_PROFILE_UPDATES_FROM_ANY_SERVER:-true} \
                                    upsp=${ALLOW_SERVICE_PROFILE_UPDATES_FROM_ANY_SERVER:-true} \
                                    upscr=${ALLOW_SCRIPT_UPDATES_FROM_ANY_SERVER:-true} \
                                    uphlp=${ALLOW_HELP_UPDATES_FROM_ANY_SERVER:-true} \
                                    upres=${ALLOW_RESOURCE_UPDATES_FROM_ANY_SERVER:-true} \
                                    uploc=${ALLOW_LOCALIZATION_UPDATES_FROM_ANY_SERVER:-true} \
                                    upal=${AUTHORIZED_SERVER_LIST} \
                                    rsc=${RESTRICT_SERVER_CERT_STORE:-false} \
                                    orc=${OCSP_REVOCATION:-false}

if [ -f ${BINDIR}/manifesttool_vpn ]; then
    ${BINDIR}/manifesttool_vpn -i ${INSTPREFIX} ${INSTPREFIX}/ACManifestVPN.xml
fi

if [ -f ${BINDIR}/manifesttool_dart ]; then
    ${BINDIR}/manifesttool_dart -i ${INSTPREFIX} ${INSTPREFIX}/ACManifestDART.xml
fi

if [ -f ${BINDIR}/manifesttool_iseposture ]; then
    ${BINDIR}/manifesttool_iseposture -i ${INSTPREFIX} ${INSTPREFIX}/ACManifestISEPosture.xml
fi

if [ -f ${BINDIR}/manifesttool_posture ]; then
    ${BINDIR}/manifesttool_posture -i ${INSTPREFIX} ${INSTPREFIX}/ACManifestPOS.xml
fi