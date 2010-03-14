#!/bin/bash
#bzr-setup.sh
# Description: Setup bzr and gets a branch of libbash-ccorp
# WARNING:	Update the bzr checkout at /var/www/bzr-setup on
#			server01.rs.clearcorp.co.cr when you update this file.
#			In order to do this, run /var/www/bzr-make.sh
#			If you make structure changes update bzr-make.sh

LIBBASH_CCORP_DIR="/usr/local/share/libbash-ccorp"

# Libraries import
. main-lib/checkRoot.sh
. main-lib/getDist.sh
. main-lib/setSources.sh

# Check user is root
checkRoot

function setSymlinks {
	rm /usr/local/sbin/ccorp-openerp-install
	ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-install/openerp-install.sh /usr/local/sbin/ccorp-openerp-install
	rm /usr/local/sbin/ccorp-ubuntu-server-install
	ln -s $LIBBASH_CCORP_DIR/install-scripts/ubuntu-server-install/ubuntu-server-install.sh /usr/local/sbin/ccorp-ubuntu-server-install
	rm /usr/local/sbin/ccorp-bzr-make
	ln -s $LIBBASH_CCORP_DIR/install-scripts/bzr-install/bzr-make.sh /usr/local/sbin/ccorp-bzr-make
}

echo "Bzr and libbash-ccorp installation script"
echo ""

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
	echo "Installing bzr..."
	echo ""
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
	read -p "Do you want to install libbash-ccorp (Y/n)? " -n 1
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	echo "Installing libbash-ccorp..."
	echo ""
	if [ $(cat /etc/environment | grep -c LIBBASH_CCORP_DIR) == 0 ]; then
		echo 'LIBBASH_CCORP_DIR="/usr/local/share/libbash-ccorp"' >> /etc/environment
	else
		sed -i "s#LIBBASH_CCORP_DIR.*#LIBBASH_CCORP_DIR=\"/usr/local/share/libbash-ccorp\"#g" /etc/environment
	fi
	if [ -d /usr/local/share/libbash-ccorp ]; then
		echo "bzr repository: /usr/local/share/libbash-ccorp already exists."
		echo "Updating..."
		cd /usr/local/share/libbash-ccorp
		bzr update
	else
		#Make libbash-ccorp dir
		mkdir /usr/local/share/libbash-ccorp
		cd /usr/local/share/libbash-ccorp
		
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
			bzr checkout --lightweight http://server01.rs.clearcorp.co.cr/bzr/libbash-ccorp/stable /usr/local/share/libbash-ccorp
		else
			bzr checkout --lightweight http://server01.rs.clearcorp.co.cr/bzr/libbash-ccorp/trunk /usr/local/share/libbash-ccorp
		fi
	fi
	setSymlinks
fi
echo ""
