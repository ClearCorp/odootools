#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    # Exits with return = 1 if user is not root.
    echo "This script must be executed as root."
    exit 1
fi

if [[ ! -d $1 ]]; then
    echo "First argument must be the actual data directory."
    exit 2
fi

if [[ ! -b $2 ]]; then
    echo "Second argument must be the new partion."
    exit 3
fi

DATADIR=$(readlink -f $1)
DEVICE=$2

#Stop postgres
service postgresql stop

#Make temp dir
TEMP=$(mktemp -d)

#Mount device in temp dir
/usr/share/google/safe_format_and_mount -m "mkfs.ext4 -F" $DEVICE $TEMP

#Move all data to the new device
rsync -axv ${DATADIR}/ ${TEMP}/

#Remove all data in datadir
rm -r ${DATADIR}/*

#Unmount device and remount in datadir
umount $DEVICE
/usr/share/google/safe_format_and_mount -m "mkfs.ext4 -F" $DEVICE $DATADIR

#Start postgres
service postgresql start
