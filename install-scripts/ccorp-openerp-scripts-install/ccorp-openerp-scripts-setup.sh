#!/bin/bash
#ccorp-openerp-scripts-setup.sh
# Description: Setup bzr and gets a branch of openerp-ccorp-scripts
# WARNING:	Update the bzr checkout at /var/www/ccorp-openerp-scripts-setup on
#			server01.rs.clearcorp.co.cr when you update this file.
#			In order to do this, run /var/www/ccorp-openerp-scripts-make.sh
#			If you make structure changes update ccorp-openerp-scripts-make.sh

OPENERP_CCORP_DIR="/usr/local/share/openerp-ccorp-scripts"

# Libraries import
. ../../main-lib/checkRoot.sh
. ../../main-lib/getDist.sh
. ../../main-lib/setSources.sh

# Check user is root
checkRoot

echo "Bzr and openerp-ccorp-scripts installation script"
echo ""

dist=""
getDist dist

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
	apt-get -y update
	apt-get -y install bzr
fi
echo ""

# Setup bzr repository
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to install openerp-ccorp-scripts (Y/n)? " -n 1
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	echo "Installing openerp-ccorp-scripts..."
	echo ""
	if [ $(cat /etc/environment | grep -c OPENERP_CCORP_DIR) == 0 ]; then
		echo 'OPENERP_CCORP_DIR="/usr/local/share/openerp-ccorp-scripts"' >> /etc/environment
	else
		sed -i "s#OPENERP_CCORP_DIR.*#OPENERP_CCORP_DIR=\"/usr/local/share/openerp-ccorp-scripts\"#g" /etc/environment
	fi
	dir=$(pwd)
	if [ -d /usr/local/share/openerp-ccorp-scripts ]; then
		echo "bzr repository: /usr/local/share/openerp-ccorp-scripts already exists."
		echo "Updating..."
		cd /usr/local/share/openerp-ccorp-scripts
		bzr pull
	else
		# Removed the choice, the trunk isn't updated anymore, only install from stable
		#------------------------------------------------------------------------------
		#Chose the branch to install
		#REPLY='none'
		#while [[ ! $REPLY =~ ^[SsTt]$ ]]; do
		#	read -p "Do you want to install openerp-ccorp-scripts stable or trunk (S/t)? " -n 1
		#	if [[ $REPLY == "" ]]; then
		#		REPLY="s"
		#	fi
		#	echo ""
		#done
		#if [[ $REPLY =~ ^[Ss]$ ]]; then
		#	branch=stable
		#else
		#	branch=trunk
		#fi

		branch=stable

		mkdir -p /etc/openerp-ccorp-scripts
		bzr branch lp:~clearcorp-drivers/oerptools/${branch} /usr/local/share/openerp-ccorp-scripts
		cat > /etc/openerp-ccorp-scripts/settings.cfg <<EOF
repo="lp:~clearcorp-drivers/oerptools"
branch=$branch
EOF
	fi
	cd $dir
	. ccorp-openerp-scripts-update.sh
	echo "If this is the first time you are running this script, please run 'export OPENERP_CCORP_DIR=/usr/local/share/openerp-ccorp-scripts'"
fi
echo ""
