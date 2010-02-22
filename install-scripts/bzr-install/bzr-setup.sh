#!/bin/bash
#bzr-setup.sh
# Description: Setup bzr and gets a branch of libbash-ccorp
# WARNING:	Update the bzr checkout at /var/www/bzr-setup on
#			server01.rs.clearcorp.co.cr when you update this file.
#			In order to do this, run /var/www/bzr-make.sh

# Libraries import
. ../../main-lib/checkRoot.sh
. ../../main-lib/getDist.sh
. ../../main-lib/setSources.sh

# Check user is root
checkRoot

# Instals bzr
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to install bzr (Y/n)? " -n 1
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	dist=""
	getDist dist
	setSources_bazaar $dist
	apt-get -y update
	apt-get -y install bzr
fi
echo ""

# Setup bzr repository
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to setup ClearCorp default repository (Y/n)? " -n 1
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	if [ -d /var/lib/bzr ]; then
		echo "Error cannot setup bzr repository: /var/lib/bzr already exists."
	else
		#Choose if you want working trees
		REPLY='none'
		while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
			read -p "Do you want working trees by default (Y/n)? " -n 1
			if [[ $REPLY == "" ]]; then
				REPLY="y"
			fi
			echo ""
		done
		cd /var/lib
		if [[ $REPLY =~ ^[Yy]$ ]]; then
			bzr init-repo bzr
		else
			bzr init-repo --no-trees
		fi
		
		#Make symbolic link to /var/lib/bzr
		ln -s /var/lib/bzr /bzr
		
		#Make libbash-ccorp dir
		mkdir /var/lib/bzr/libbash-ccorp
		cd /var/lib/bzr/libbash-ccorp
		
		#Chose the branch to install
		REPLY='none'
		while [[ ! $REPLY =~ ^[SsTt]$ ]]; do
			read -p "Do you want to install libbash-ccorp stable or trunk (S/t)? " -n 1
			if [[ $REPLY == "" ]]; then
				REPLY="s"
			fi
			echo ""
		done
		if [[ $REPLY =~ ^[Ss]$ ]]; then
			bzr branch http://server01.rs.clearcorp.co.cr/bzr/libbash-ccorp/stable
		else
			bzr branch http://server01.rs.clearcorp.co.cr/bzr/libbash-ccorp/trunk
		fi
	fi
fi
echo ""
