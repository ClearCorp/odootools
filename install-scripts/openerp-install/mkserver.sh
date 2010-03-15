#       mkserver.sh
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

# Print title
log_echo "OpenERP make server script"
log_echo "--------------------------"
log_echo ""

name=""
while [[ $name == "" ]]; do
	read -p "Enter the OpenERP server name: " name
	if [[ $name == "" ]]; then
		log_echo "The name cannot be blank."
	fi
done

#~ Set the openerp port
if [[ ! -f /etc/openerp/ports ]]; then
	mkdir -p /etc/openerp
	touch /etc/openerp/ports
fi
port=""
test="^[0-9]{2}$"
while [[ $port == "" ]]; do
	read -p "Enter the OpenERP server port (2 digits only): " port
	if [[ ! $port =~ $test ]]; then
		log_echo "The port has to contain exactly 2 digits."
		port=""
	elif [[ `grep -c $port /etc/openerp/ports` != 0 ]]; then
		log_echo "The port $port is already in use (/etc/openerp/ports)."
		port=""
	fi
done
echo $port >> /etc/openerp/ports
log_echo "Selected port is: $port"

#~ Set the openerp admin password
admin_passwd=""
while [[ $admin_passwd == "" ]]; do
	read -p "Enter the OpenERP administrator password: " admin_passwd
	if [[ $admin_passwd == "" ]]; then
		log_echo "The password cannot be empty."
	else
		read -p "Enter the OpenERP administrator password again: " admin_passwd2
		log_echo ""
		if [[ $admin_passwd == $admin_passwd2 ]]; then
			log_echo "OpenERP administrator password set."
		else
			admin_passwd=""
			log_echo "Passwords don't match."
		fi
	fi
	log_echo ""
done

#~ Set the server type
type=$(cat /etc/openerp/type)

log_echo "Copying openerp-server files..."
cp -a /usr/local/lib/python2.6/dist-packages/openerp-server-skeleton /usr/local/lib/python2.6/dist-packages/openerp-server-$name

log_echo "Creating openerp-server init script..."
cp -a /etc/openerp/server/init-skeleton /etc/init.d/openerp-server-$name
sed -i "s#\\[NAME\\]#$name#g" /etc/init.d/openerp-server-$name
update-rc.d openerp-server-$name defaults >> $INSTALL_LOG_FILE

log_echo "Creating openerp-server bin script..."
cp -a /etc/openerp/server/bin-skeleton /usr/local/bin/openerp-server-$name
sed -i "s#\\[NAME\\]#$name#g" /usr/local/bin/openerp-server-$name

log_echo "Creating openerp-server configuration file..."
cp -a /etc/openerp/server/server.conf-skeleton /etc/openerp/server/$name.conf
sed -i "s#\\[NAME\\]#$name#g" /etc/openerp/server/$name.conf
sed -i "s#\\[XMLPORT\\]#20$port#g" /etc/openerp/server/$name.conf
sed -i "s#\\[NETPORT\\]#21$port#g" /etc/openerp/server/$name.conf
sed -i "s#\\[ADMIN_PASSWD\\]#$admin_passwd#g" /etc/openerp/server/$name.conf

log_echo "Creating openerp-server log files..."
mkdir -p /var/log/openerp/$name
touch /var/log/openerp/$name/server.log


log_echo "Creating openerp-web init script..."
cp -a /etc/openerp/web-client/init-skeleton /etc/init.d/openerp-web-$name
sed -i "s#\\[NAME\\]#$name#g" /etc/init.d/openerp-web-$name
update-rc.d openerp-web-$name defaults >> $INSTALL_LOG_FILE

log_echo "Creating openerp-web configuration file..."
cp -a /etc/openerp/web-client/web-client.conf-skeleton /etc/openerp/web-client/$name.conf
sed -i "s#\\[NAME\\]#$name#g" /etc/openerp/web-client/$name.conf
sed -i "s#\\[PORT\\]#22$port#g" /etc/openerp/web-client/$name.conf
sed -i "s#\\[SERVER_PORT\\]#21$port#g" /etc/openerp/web-client/$name.conf
if [[ $type != "develpment" ]]; then
	sed -i "s/#\?[[:space:]]*\(dbbutton\.visible.*\)/dbbutton.visible = False/g" /etc/openerp/web-client/$name.conf
fi
sed -i "s#\\[TYPE\\]#$type#g" /etc/openerp/web-client/$name.conf

log_echo "Creating openerp-web log files..."
touch /var/log/openerp/$name/web-client-access.log
touch /var/log/openerp/$name/web-client-error.log
chown -R openerp:root /var/log/openerp/$name

log_echo "Creating apache rewrite file..."
cp -a /etc/openerp/apache2/ssl-skeleton /etc/openerp/apache2/rewrites/$name
sed -i "s#\\[NAME\\]#$name#g" /etc/openerp/apache2/rewrites/$name
sed -i "s#\\[PORT\\]#22$port#g" /etc/openerp/apache2/rewrites/$name
service apache2 reload >> $INSTALL_LOG_FILE

log_echo "Creating pid dir..."
mkdir -p /var/run/openerp/$name
chown openerp:root /var/run/openerp/$name
