#       rmserver.sh
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

if [[ ! -d $LIBBASH_CCORP_DIR ]]; then
	echo "libbash-ccorp not installed."
	exit 1
fi

#~ Libraries import
. $LIBBASH_CCORP_DIR/main-lib/checkRoot.sh
. $LIBBASH_CCORP_DIR/main-lib/getDist.sh
. $LIBBASH_CCORP_DIR/install-scripts/openerp-install/openerp-lib.sh

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
log_echo "OpenERP remove server script"
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
		read -p "You have installed versions 5 and 6, choose the version for server to remove (5/_6_): " branch
		if [[ $branch == "" ]]; then
			branch="6"
		fi
		log_echo ""
	done
fi

if [[ $branch =~ ^[5]$ ]]; then
	log_echo "This server is on 5.0 branch."
	branch="5.0"
else
	log_echo "This server is on 6.0 branch."
	branch="6.0"
fi

name=""
while [[ $name == "" ]]; do
	read -p "Enter the OpenERP server name to remove: " name
	if [[ $name == "" ]]; then
		log_echo "The name cannot be blank."
	elif [[ ! -d /srv/openerp/$branch/instances/$name ]]; then
		log_echo "The server: $name doesn't exist. Please enter a valid server name."
		name=""
	fi
done

#~ Remove the openerp port
log_echo "Removing openerp port..."
rm /etc/openerp/ports/*_$name >> $INSTALL_LOG_FILE

#~ Stop the server
log_echo "Stopping openerp server and web..."
/etc/init.d/openerp-server-$name stop >> $INSTALL_LOG_FILE
/etc/init.d/openerp-web-$name stop >> $INSTALL_LOG_FILE

# Remove init scripts
log_echo "Removing openerp init scripts..."
rm /etc/init.d/openerp-server-$name >> $INSTALL_LOG_FILE
rm /etc/init.d/openerp-web-$name >> $INSTALL_LOG_FILE
update-rc.d openerp-server-$name disable >> $INSTALL_LOG_FILE
update-rc.d openerp-web-$name disable >> $INSTALL_LOG_FILE

# Delete openerp postgres user
log_echo "Deleting user..."
/usr/bin/sudo -u postgres dropuser openerp_$name >> $INSTALL_LOG_FILE
deluser openerp_$name >> $INSTALL_LOG_FILE
log_echo ""

log_echo "Removing instance..."
rm -r /srv/openerp/$branch/instances/$name >> $INSTALL_LOG_FILE

log_echo "Removing openerp-server bin script..."
rm /usr/local/bin/openerp-server-$name >> $INSTALL_LOG_FILE

log_echo "Removing openerp-server configuration file..."
rm /etc/openerp/$branch/server/$name.conf >> $INSTALL_LOG_FILE

log_echo "Removing openerp-server ssl files..."
rm /etc/openerp/ssl/servers/$name.* >> $INSTALL_LOG_FILE
rm /etc/openerp/ssl/servers/${name}_crt.pem >> $INSTALL_LOG_FILE
rm /etc/openerp/ssl/servers/${name}_key.pem >> $INSTALL_LOG_FILE

log_echo "Removieng log files..."
rm -r /var/log/openerp/$name/ >> $INSTALL_LOG_FILE

log_echo "Removing openerp-web bin script..."
rm /usr/local/bin/openerp-web-$name >> $INSTALL_LOG_FILE

log_echo "Removing openerp-web configuration file..."
rm /etc/openerp/$branch/web-client/$name.conf

log_echo "Removing apache rewrite file..."
rm /etc/openerp/apache2/rewrites/$name
service apache2 reload >> $INSTALL_LOG_FILE

log_echo "Removing pid dir..."
rm -r /var/run/openerp/$name

exit 0
