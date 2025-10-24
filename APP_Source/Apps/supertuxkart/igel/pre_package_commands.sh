#!/bin/bash

# libopenal.so.1.19.1 wants libsndio.so.7.0 which ldconfig cache cannot find
patchelf --set-rpath '/services/supertuxkart/usr/lib/x86_64-linux-gnu' '%root%/usr/lib/x86_64-linux-gnu/libopenal.so.1.19.1'