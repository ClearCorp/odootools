#!/bin/bash
# Restore Partition tables, RAID, and LVM'S previously backed up 


#############FUNCTIONS###########

## determines if string $1 exists in any position of the array $2

function existsinarray
{
array=$2
for arrayval in ${array[@]}
        do
        if  [[ "$arrayval" == "$1" ]];
                then
                return 1
                fi
        done
return 0
}
#############FUNCTIONS###########


## Restore of partition tables from files "backed-up-files/sd*.mbr"

#for f in backed-up-files/sd*; do

T=${f##*/}
echo "restoring partition table from device: ${T%.*}"
dd  if=$f of=/dev/${T%.*} bs=512 count=1
#partprobe

#done



# Parsing backed-up-files/RAID.conf so it has form of commands

echo "Parsing backed-up-files/RAID.conf"

cp backed-up-files/RAID.conf backed-up-files/RAID.conf.old
sed -i 's/ARRAY[[:space:]]*/mdadm create /g' backed-up-files/RAID.conf
sed -i 's/UUID=[[:alnum:]]*:[[:alnum:]]*:[[:alnum:]]*:[[:alnum:]]*/ /g' backed-up-files/RAID.conf
sed -i 's/[[:space:]]*level/ --level/g' backed-up-files/RAID.conf
sed -i 's/[[:space:]]*num/ --num/g' backed-up-files/RAID.conf
sed -i 's/[[:space:]]*spares/ --spares/g' backed-up-files/RAID.conf
sed -i 's/[[:space:]]*[[:space:]]devices/ --devices/g' backed-up-files/RAID.conf
cat backed-up-files/RAID.conf | tr '\n' ' ' > backed-up-files/RAID.conf
sed -i 's/mdadm/\nmdadm/g' backed-up-files/RAID.conf
sed '/^$/d' backed-up-files/RAID.conf > backed-up-files/RAID.conf.clean
echo  >>    backed-up-files/RAID.conf.clean
mv backed-up-files/RAID.conf.clean backed-up-files/RAID.conf


# Restores MD devices specified in backed-up-files/RAID.conf 

#exec < backed-up-files/RAID.conf

echo "Restoring MD devices"
while read line
	do
	$line
	done



#creates volume groups and adds the physical volumes to them
exec < backed-up-files/pvs.conf

declare -a arrayvgs

while read line
	do
		pv=${line%%;*}
		templine=${line#*;}
		vg=${templine%%;*}

		existsinarray $vg $arrayvgs
		result=$?
		
		if [ "$result" -eq 0  ]; then
		pos=${#arrayvgs[@]}
		arrayvgs[$pos]=${vg}
		echo "Creating volume group:$vg and attaching physical volume:$pv"

		vgcreate $vg $pv

		else

		echo "Extending volume group:$vg with physical volume:$pv"
		vgextend $vg $pv
		fi

	done


## Creates logical volumes specified in backed-up-files/lvs.conf
## ommiting snapshots

exec <backed-up-files/lvs.conf

	while read line
	do
		lv=${line%%;*}
                templine=${line#*;}
                vg=${templine%%;*}
		templine=${templine#*;}
		attr=${templine%%;*}
		templine=${templine#*;}
		size=${templine%%;*}
#		echo "lv |$lv| vg |$vg| attr |$attr| size |$size|"
		
		snapchar=${attr:0:1}	
			if [[ "$snapchar" != "s"  ]];then
			
			echo "Creating logical volume $lv"
			lvcreate -L $size -n $lv /dev/$vg
			lvscore=$(echo "$lv"| sed 's/-/--/g')
			fstype=$(file -s /dev/mapper/$vg-$lvscore)

			## starting to guess the filesystem type
			xfs="XFS"
			ext3="ext3"
			ext4="ext4"
			reiser="ReiserFS"
			swap="swap"
			
			if [[ "$fstype" =~ "${xfs}" ]];then
			echo "Creating filesystem type XFS"					
			mkfs.xfs /dev/$vg/$lv
			fi
			
			if [[ "$fstype" =~ "${ext3}" ]];then
			echo "Creating filesystem type ext3"
			mkfs.ext3 /dev/$vg/$lv
			fi

			if [[ "$fstype" =~ "${ext4}" ]];then
			echo "Creating filesystem type ext4"					
			mkfs.ext4 /dev/$vg/$lv
			fi

			if [[ "$fstype" =~ "${reiser}" ]];then
			echo "Creating filesystem type ReiserFS"					
			mkfs.reiserfs /dev/$vg/$lv
			fi

			if [[ "$fstype" =~ "${swap}" ]];then
			echo "Creating swap"					
			mkswap /dev/$vg/$lv
			fi

			fi
		
	done




exit 0
