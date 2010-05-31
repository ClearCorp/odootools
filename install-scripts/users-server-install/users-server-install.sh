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
	read -p "What is your server FQDN (`hostname --fqdn`)? " fqdn
	if [[ $fqdn == "" ]]; then
		fqdn=$(hostname --fqdn)
	fi
	echo ""
done
host_name=`echo $fqdn | grep -oe "^[^.]*"`

# Enter mail domain
while [[ $main_domain == "" ]]; do
	read -p "What is your mail server public domain name ($fqdn)? " main_domain
	if [[ $main_domain == "" ]]; then
		main_domain=$fqdn
	fi
	echo ""
done

# Enter LDAP suffix
while [[ $ldap_suffix == "" ]]; do
	read -p "What is your LDAP root suffix (dc=example,dc=com)? " ldap_suffix
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
if [[ `hostname --fqdn` == $fqdn ]]; then
	log_echo "Hostname: $fqdn"
else
	log_echo "Please reboot and run this script again."
fi

# Fix for iRedMail
export TERM='linux'

# 
cd $src_path
wget http://iredmail.googlecode.com/files/iRedMail-${IREDMAIL_VER}.tar.bz2
tar jxvf iRedMail-${IREDMAIL_VER}.tar.bz2
cd iRedMail-${IREDMAIL_VER}/pkgs/
bash get_all.sh

# Lucid fixes
cd ..
sed -i "s/mysql-server-5\\.0 mysql-client-5\\.0/mysql-server-5.1 mysql-client-5.1/g" functions/packages.sh
sed -i "s/mailx/mailutils/g" functions/packages.sh
log_echo "Se va a instalar postfix-policyd, durante la instalación se solicitará una contraseña. Es necesario escribir alguna, después se volverá a poner en blanco automáticamente."
mysql_temp_passwd=""
while [[ $mysql_temp_passwd == "" ]]; do
	read -p "Enter the temporary MySQL password: " mysql_temp_passwd
	if [[ $mysql_temp_passwd == "" ]]; then
		log_echo "The password cannot be empty."
	else
		read -p "Enter the temporary MySQL password again: " mysql_temp_passwd2
		log_echo ""
		if [[ $mysql_temp_passwd == $mysql_temp_passwd2 ]]; then
			log_echo "Temporary MySQL password set. Write the SAME when asked."
		else
			mysql_temp_passwd=""
			log_echo "Passwords don't match."
		fi
	fi
	log_echo ""
done
apt-get -qqy install postfix-policyd
echo 'grant all privileges on *.* to root@localhost identified by ""; flush privileges;' | mysql --user=root --pass=$mysql_temp_passwd

cp $LIBBASH_CCORP_DIR/install-scripts/users-server-install/managesieve.sh functions/
chown 501:80 functions/managesieve.sh

# Install iRedMail
bash iRedMail.sh

# phpLDAPadmin fix
sed -i "s/protected function draw_dn(\$dn,\$level=0,\$first_child=true,\$last_child=true)/protected function draw_dn(\$dn,\$level,\$first_child=true,\$last_child=true)/g" /usr/share/apache2/phpldapadmin/lib/AJAXTree.php

exit 0