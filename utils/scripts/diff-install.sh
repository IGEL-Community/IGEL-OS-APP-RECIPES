#!/bin/bash
#set -x
#trap read debug

# file listing before install
pushd .
cd /
#sudo sh -c 'find bin etc home lib opt sbin usr var -type f | sort > /tmp/find_root_listing1.txt'
sudo sh -c 'find bin etc home lib opt sbin usr var | sort > /tmp/find_root_listing1.txt'
popd

# do install
#sample cp for testing
cp $0 new-diff-install-me.txt

# file listing after install
pushd .
cd /
#sudo sh -c 'find bin etc home lib opt sbin usr var -type f | sort > /tmp/find_root_listing2.txt'
sudo sh -c 'find bin etc home lib opt sbin usr var | sort > /tmp/find_root_listing2.txt'
popd

# tar file of the new files
pushd .
cd /
#sudo sh -c 'comm -1 -3 /tmp/find_root_listing1.txt /tmp/find_root_listing2.txt | xargs tar -cjvf /tmp/newfiles.tar.bz2'
sudo sh -c 'comm -1 -3 /tmp/find_root_listing1.txt /tmp/find_root_listing2.txt > /tmp/find_new_items.txt'
