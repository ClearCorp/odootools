#!/bin/bash

#       koo-install.sh
#       
#       Copyright 2010 ClearCorp S.A. <info@clearcorp.co.cr>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

if [[ ! -d $OPENERP_CCORP_DIR ]]; then
	echo "openerp-ccorp-scripts not installed."
	exit 1
fi

#~ Libraries import
. $OPENERP_CCORP_DIR/main-lib/checkRoot.sh
. $OPENERP_CCORP_DIR/main-lib/getDist.sh

# Check user is root
checkRoot

# Init log file
INSTALL_LOG_PATH=/var/log/openerp
INSTALL_LOG_FILE=$INSTALL_LOG_PATH/koo-install.log

if [[ ! -f $INSTALL_LOG_FILE ]]; then
	mkdir -p $INSTALL_LOG_PATH
	touch $INSTALL_LOG_FILE
fi

function log {
	echo "$(date): $1" >> $INSTALL_LOG_FILE
}
function log_echo {
	echo $1
	log "$1"
}
log ""

# Print title
log_echo "Koo installation script"
log_echo "---------------------------"
log_echo ""

# Set distribution
dist=""
getDist dist
log_echo "Distribution: $dist"
log_echo ""

# Sets vars corresponding to the distro
if [[ $dist == "lucid" ]]; then
	# Ubuntu 10.04, python 2.6
	posgresql_rel=8.4
	python_rel=python2.6
	ubuntu_rel=10.04
	base_path=/usr/local
	install_path=$base_path/lib/$python_rel/dist-packages
	sources_path=$base_path/src
elif [[ $dist == "maverick" ]]; then
	# Ubuntu 10.10, python 2.6
	posgresql_rel=8.4
	python_rel=python2.6
	ubuntu_rel=10.10
	base_path=/usr/local
	install_path=$base_path/lib/$python_rel/dist-packages
	sources_path=$base_path/src
else
	# Only Karmic supported for now
	log_echo "ERROR: This program must be executed on Ubuntu Lucid 10.04 (Desktop or Server)"
	exit 1
fi

#~ Select user
openerp_user=""
while [[ $openerp_user == "" ]]; do
	read -p "What is the developer username? " openerp_user
	if [[ $openerp_user == "" ]]; then
		echo "Please enter a valid username."
	elif [[ `cat /etc/passwd | grep -c $openerp_user` == 0 ]]; then
		echo "Please enter a valid username."
		openerp_user=""
	fi
	log_echo ""
done

#Download
#########

log_echo "Preparing installation"
log_echo "----------------------"

# Update the system.
log_echo "Updating the system..."
apt-get -qq update >> $INSTALL_LOG_FILE
apt-get -qqy upgrade >> $INSTALL_LOG_FILE
log_echo ""

# Install the required python libraries for openerp-server.
echo "Installing the required python libraries for koo..."
apt-get -qqy install python-qt4 python-dbus python-qt4-dbus pyro >> $INSTALL_LOG_FILE
log_echo ""

log_echo "Downloading Koo"
log_echo "-------------------"
log_echo ""

cd $sources_path

# Download nan-tic modules
log_echo "Downloading nan-tic modules..."
bzr checkout --lightweight http://bazaar.launchpad.net/~openobject-client-kde/openobject-client-kde/$branch openobject-client-kde >> $INSTALL_LOG_FILE
cd openobject-client-kde
bzr update >> $INSTALL_LOG_FILE
log_echo ""


# Install OpenERP
#################

log_echo "Installing Koo"
log_echo "------------------"
log_echo ""

cd $sources_path

# Install Koo
log_echo "Installing Koo..."
cd openobject-client-kde
make install >> $INSTALL_LOG_FILE
sed -i "s#/usr/lib/python2\\.6/dist-packages/Koo#/usr/local/lib/python2.6/dist-packages/Koo#g" /usr/local/bin/koo
cp -a Koo/* $install_path/Koo/
cat > /home/$openerp_user/.local/share/applications/koo.desktop << EOF
[Desktop Entry]
Version=1.0
Terminal=false
Exec=koo
Icon=/usr/local/share/Koo/ui/koo-icon.png
Type=Application
InitialPreference=6
Categories=Application;Office;
StartupNotify=false
Name=Koo
GenericName=OpenERP KDE client
Comment=OpenERP KDE client
EOF

chown $openerp_user:$openerp_user /home/$openerp_user/.local/share/applications/koo.desktop


exit 0
