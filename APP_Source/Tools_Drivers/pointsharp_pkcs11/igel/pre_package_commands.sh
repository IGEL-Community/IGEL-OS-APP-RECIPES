#!/bin/bash

mkdir -p "%root%/etc/pkcs11.d"
cat <<EOF > "%root%/etc/pkcs11.d/pkcs11_template.json"
{
    "name": "pkcs11_template smartcard framework",
    "libpath": "/usr/lib/pkcs11_template.so"
}
EOF
