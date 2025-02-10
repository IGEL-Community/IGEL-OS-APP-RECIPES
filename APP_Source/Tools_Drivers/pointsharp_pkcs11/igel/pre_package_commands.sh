#!/bin/bash

mkdir -p "%root%/etc/pkcs11.d"
cat <<EOF > "%root%/etc/pkcs11.d/%name%.json"
{
    "name": "%summary%",
    "libpath": "%libpath%"
}
EOF
