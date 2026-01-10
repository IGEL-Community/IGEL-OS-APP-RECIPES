#!/bin/bash
#set -x
#trap read debug

echo "The OS Version is: " $(igelpkgctl list installed | grep base_system | tr -d '\t')
