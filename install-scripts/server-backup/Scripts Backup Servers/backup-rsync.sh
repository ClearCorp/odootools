#!/bin/bash
# backup-rsync.sh
# Creates a backup from the logical volumes data specified in files/lvs.list and
# boot partition specified in files/boot.list
# in directory specified in files/backup-path.list

function backuplv () {
	line="$1"
	backpath="$2"
	size=${line#*	} 	# gets size for the new volume 
	line=${line%	*}	# set line as the rest 
	vg=${line%/*}		# gets volume group name
	lv=${line#*/}		# gets logical volume
echo	""
echo	""
echo	"Making backup of logical volume: $lv"
echo	""

lvcreate -s -n $lv-backup-snap -L $size $line
mkdir /media/$lv-backup
mount  /dev/$line-backup-snap /media/$lv-backup 
retcode="$?"
	if [ "$retcode" -ne 0 ]; then
	sleep 4
	echo "MOUNT FAILED, must be xfs file system, trying with nouuid"
	mount -o nouuid /dev/$line-backup-snap /media/$lv-backup 
	fi
	

mkdir -p $backpath$lv 
rsync -axv --delete /media/$lv-backup/ $backpath$lv
umount /media/$lv-backup
rm -r /media/$lv-backup
lvremove -f $line-backup-snap

return 0
}

function backuppartition () {
	line="$1"
	backpath="$2"
echo	""
echo	""
echo	"Making backup of boot partition"
echo	""

mkdir /media/boot-backup
mount  ${line} /media/boot-backup 
mkdir -p ${backpath}boot
rsync -axv --delete /media/boot-backup/ ${backpath}boot 
umount /media/boot-backup
rm -r /media/boot-backup

return 0
}

# Reads the path where the backup will be stored
exec < files/backup-path.list
	read backuppath 

# Reads the logical volumes that will be backed up
exec < files/lvs.list
	while read line
		do
		hash=${line:0:1}	# set hash with the first character of the line 
			if [[ "$hash" == "#" ]]; then
			echo "es comment"
			else
			backuplv "$line"  "$backuppath"
			
			fi

		done

# Reads the boot partition and saves the information
exec < files/boot.list
	read line
	backuppartition "$line" "$backuppath"

