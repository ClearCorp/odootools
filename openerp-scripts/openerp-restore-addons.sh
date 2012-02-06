#       openerp-restore-addons.sh
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
#!/bin/bash

if [[ ! -d $OPENERP_CCORP_DIR ]]; then
	echo "openerp-ccorp-scripts not installed."
	exit 1
fi

#~ Libraries import
. $OPENERP_CCORP_DIR/main-lib/checkRoot.sh
. $OPENERP_CCORP_DIR/main-lib/getDist.sh
. $OPENERP_CCORP_DIR/openerp-scripts/openerp-lib.sh

# Check user is root
checkRoot

# Init log file
INSTALL_LOG_PATH=/var/log/openerp
INSTALL_LOG_FILE=$INSTALL_LOG_PATH/install.log

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

# Set distribution
dist=""
getDist dist
log_echo "Distribution: $dist"
log_echo ""

openerp_get_dist

# Print title
log_echo "OpenERP update addons script"
log_echo "----------------------------"
log_echo ""

# Source installation variables
if [ -d /etc/openerp/5.0 ] && [ ! -d /etc/openerp/6.0 ]; then
	branch="5"
elif [ ! -d /etc/openerp/5.0 ] && [ -d /etc/openerp/6.0 ]; then
	branch="6"
else
	branch=""
	while [[ ! $branch =~ ^[56]$ ]]; do
		read -p "You have installed versions 5 and 6, choose the version for this server instance (5/_6_): " branch
		if [[ $branch == "" ]]; then
			branch="6"
		fi
		log_echo ""
	done
fi

if [[ $branch =~ ^[5]$ ]]; then
	log_echo "This server will use 5.0 branch."
	branch="5.0"
else
	log_echo "This server will use 6.0 branch."
	branch="6.0"
fi

. /etc/openerp/$branch/install.cfg

name=""
while [[ $name == "" ]]; do
	read -p "Enter the OpenERP server name: " name
	if [[ $name == "" ]]; then
		log_echo "The name cannot be blank."
	elif [[ ! -d /srv/openerp/instances/$name ]]; then
		log_echo "There isn't any instance named $name"
		name=""
	fi
done

log_echo "Restoring addons for $name"
mkserver_addons_rm_links
mkserver_install_addons


exit 0
