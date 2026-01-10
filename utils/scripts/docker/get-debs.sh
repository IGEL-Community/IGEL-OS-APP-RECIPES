#!/bin/bash
#set -x
#trap read debug

# Update MISSING_LIBS - example for kmag screen magnifier
MISSING_LIBS="kio kmag libkf5archive5 libkf5authcore5 libkf5codecs5 libkf5configcore5 libkf5configgui5 libkf5configwidgets5 libkf5coreaddons5 libkf5crash5 libkf5dbusaddons5 libkf5globalaccel5 libkf5guiaddons5 libkf5i18n5 libkf5iconthemes5 libkf5itemviews5 libkf5kiocore5 libkf5service5 libkf5widgetsaddons5 libkf5xmlgui5 libqaccessibilityclient-qt5-0 libqt5waylandclient5"

mkdir build_tar
cd build_tar

for lib in $MISSING_LIBS; do
  apt-get download $lib
  ls $lib* >> deb-listing.txt
  mv $lib*.deb $lib.deb
done

mv *.deb ..
mv deb-listing.txt ..
cd ..
rm -rf build_tar
