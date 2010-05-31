#       users-server-install.sh
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

IREDMAIL_VER='0.5.1'

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
INSTALL_LOG_PATH=/var/log/users-server
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
log_echo "Users server installation script"
log_echo "--------------------------------"
log_echo ""

# Set distribution
dist=""
getDist dist
log_echo "Distribution: $dist"
log_echo ""

# Sets vars corresponding to the distro
if [[ $dist == "lucid" ]]; then
	# Ubuntu 10.04
	ubuntu_rel=10.04
	src_path='/usr/local/src'
else
	# Only Karmic supported for now
	log_echo "ERROR: This program must be executed on Ubuntu Lucid Server 10.04 LTS"
	exit 1
fi

# Run the Ubuntu preparation script.
while [[ ! $run_preparation_script =~ ^[YyNn]$ ]]; do
	read -p "Do you want to run ccorp-ubuntu-server-install script (recommended if not already done) (y/N)? " -n 1 run_preparation_script
	if [[ $run_preparation_script == "" ]]; then
		run_preparation_script="n"
	fi
	log_echo ""
done
if [[ $run_preparation_script =~ ^[Yy]$ ]]; then
	log_echo "Running ccorp-ubuntu-server-install..."
	log_echo ""
	ccorp-ubuntu-server-install
fi


# Initial questions
####################

# Enter IP address
while [[ $ip_addr == "" ]]; do
	echo "What is your IP address (list: `ifconfig  | grep 'inet addr:'| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1}'`): "
	read -p "WARNING: IP address not verified, WRITE IT CAREFULLY!!: " ip_addr
	echo ""
done

# Enter domain
while [[ $fqdn == "" ]]; do
	read -p "What is your server FQDN (`hostname --fqdn`)?" fqdn
	echo ""
done
host_name = `echo $fqdn | grep -oe "^[^.]*"`

# Enter mail domain
while [[ $main_domain == "" ]]; do
	read -p "What is your mail server public domain name ($fqdn)?" main_domain
	echo ""
done

# Enter LDAP suffix
while [[ $ldap_suffix == "" ]]; do
	read -p "What is your LDAP root suffix (dc=example,dc=com)?" ldap_suffix
	echo ""
done


# Set the hostname and the FQDN correctly
if [[ `cat /etc/hosts | grep -c 127.0.0.1` == 0 ]]; then
	echo "127.0.0.1 $fqdn $host_name localhost localhost.localdomain" > /etc/hosts.2
	echo "$ip_addr $fqdn" >> /etc/hosts.2
	cat /etc/hosts >> /etc/hosts.2
	mv /etc/hosts.2 /etc/hosts
else
	sed -i "s/127\\.0\\.0\\.1.*/127.0.0.1 $fqdn $host_name localhost localhost.localdomain\n$ip_addr $fqdn/g" /etc/hosts
fi
echo $host_name > /etc/hostname

# Fix for iRedMail
export TERM='linux'

# 
cd $src_path
wget http://iredmail.googlecode.com/files/iRedMail-${IREDMAIL_VER}.tar.bz2
tar jxvf iRedMail-${IREDMAIL_VER}.tar.bz2
cd iRedMail-${IREDMAIL_VER}/pkgs/
bash get_all.sh

exit 0