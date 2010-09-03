#!/bin/bash
# Makes a backup of RAID configuration, partition tables 
# and logical volumes.

. lib/checkRoot.sh

checkRoot


# Saves data from RAID
mdadm --detail --scan --verbose > backed-up-files/RAID.conf


# Saves partitions specified in file files/disks.list 
exec < files/disks.list

while read line

	do
		newline="/dev/${line}" 
		dd  if=$newline of=backed-up-files/$line.mbr bs=512 count=1
		echo "Backed up device MBR from device ${newline} "
	done

# Saves physical volumes and volume groups in file backed-up-files/pvs.conf
pvs --noheading --aligned --separator ";" > backed-up-files/pvs.conf

# Saves logical volumes in file backed-up-files/lvs.conf
lvs --noheading --aligned --separator ";" > backed-up-files/lvs.conf

exit 0
