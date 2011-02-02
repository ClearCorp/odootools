#       openerp-install.sh
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

log ""

# Print title
log_echo "OpenERP installation script"
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
	install_path_web=$base_path/lib/$python_rel/dist-packages
	addons_path=$install_path/addons/
	sources_path=$base_path/src/openerp
elif [[ $dist == "maverick" ]]; then
	# Ubuntu 10.10, python 2.6
	posgresql_rel=8.4
	python_rel=python2.6
	ubuntu_rel=10.10
	base_path=/usr/local
	install_path=$base_path/lib/$python_rel/dist-packages
	install_path_web=$base_path/lib/$python_rel/dist-packages
	addons_path=$install_path/addons/
	sources_path=$base_path/src/openerp
else
	# Only Lucid supported for now
	log_echo "ERROR: This program must be executed on Ubuntu Lucid 10.04 or 10.10 (Desktop or Server)"
	exit 1
fi

# Check system values
check_system_values
if [[ $? == 1 ]]; then
	exit 1
fi


# Initial questions
####################

#~ Choose between server or working station
while [[ ! $server_type =~ ^[SsWw]$ ]]; do
	read -p "Is this a Server or a Working station (S/w)? " -n 1 server_type
	if [[ $server_type == "" ]]; then
		server_type="s"
	fi
	log_echo ""
done

if [[ $server_type =~ ^[Ww]$ ]]; then
	log_echo "This is a working station"
	server_type="station"
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
else
	#~ Choose between development and production server
	while [[ ! $server_type =~ ^[DdPp]$ ]]; do
		read -p "Is this a Development or Production server (D/p)? " -n 1 server_type
		if [[ $server_type == "" ]]; then
			server_type="d"
		fi
		log_echo ""
	done
	if [[ $server_type =~ ^[Pp]$ ]]; then
		log_echo "This is a production server"
		server_type="production"
	else
		server_type="development"
	fi
	openerp_user="openerp"
fi

#Choose the branch to install
while [[ ! $branch =~ ^[56]$ ]]; do
	read -p "Which branch do you want to install (5/_6_)? " -n 1 branch
	if [[ $branch == "" ]]; then
		branch="6"
	fi
	log_echo ""
done
if [[ $branch =~ ^[5]$ ]]; then
	log_echo "This installation will use 5.0 branch."
	branch="5.0"
else
	log_echo "This installation will use 6.0 branch."
	branch="6.0"
fi
sources_path="$sources_path-$branch"
install_path="$install_path/openerp-server-$branch-skeleton"
echo ""

#Install openerp_addons
while [[ ! $install_openerp_addons =~ ^[YyNn]$ ]]; do
        read -p "Would you like to install openerp addons (Y/n)? " -n 1 install_openerp_addons
        if [[ $install_openerp_addons == "" ]]; then
                install_openerp_addons="y"
        fi
        log_echo ""
done

#Install ccorp_addons
while [[ ! $install_ccorp_addons =~ ^[YyNn]$ ]]; do
        read -p "Would you like to install ccorp addons (Y/n)? " -n 1 install_ccorp_addons
        if [[ $install_ccorp_addons == "" ]]; then
                install_ccorp_addons="y"
        fi
        log_echo ""
done

#Install costa_rica_addons
while [[ ! $install_costa_rica_addons =~ ^[YyNn]$ ]]; do
        read -p "Would you like to install Costa Rica addons (Y/n)? " -n 1 install_costa_rica_addons
        if [[ $install_costa_rica_addons == "" ]]; then
                install_costa_rica_addons="y"
        fi
        log_echo ""
done

#Install extra-addons
while [[ ! $install_extra_addons =~ ^[YyNn]$ ]]; do
        read -p "Would you like to install extra addons (Y/n)? " -n 1 install_extra_addons
        if [[ $install_extra_addons == "" ]]; then
                install_extra_addons="y"
        fi
        log_echo ""
done

#Install magentoerpconnect
while [[ ! $install_magentoerpconnect =~ ^[YyNn]$ ]]; do
        read -p "Would you like to install magentoerpconnect (Y/n)? " -n 1 install_magentoerpconnect
        if [[ $install_magentoerpconnect == "" ]]; then
                install_magentoerpconnect="y"
        fi
        log_echo ""
done

#Install nan-tic modules
while [[ ! $install_nantic =~ ^[YyNn]$ ]]; do
        read -p "Would you like to install nan-tic modules (Y/n)? " -n 1 install_nantic
        if [[ $install_nantic == "" ]]; then
                install_nantic="y"
        fi
        log_echo ""
done

#Select FQDN
fqdn=""
while [[ $fqdn == "" ]]; do
        read -p "Enter the FQDN for this server (`hostname --fqdn`)? " fqdn
        if [[ $fqdn == "" ]]; then
                fqdn=`hostname --fqdn`
        fi
        log_echo ""
done

#Set the openerp admin password
openerp_admin_passwd=""
while [[ $openerp_admin_passwd == "" ]]; do
	read -p "Enter the OpenERP administrator password: " openerp_admin_passwd
	if [[ $openerp_admin_passwd == "" ]]; then
		log_echo "The password cannot be empty."
	else
		read -p "Enter the OpenERP administrator password again: " openerp_admin_passwd2
		log_echo ""
		if [[ $openerp_admin_passwd == $openerp_admin_passwd2 ]]; then
			log_echo "OpenERP administrator password set."
		else
			openerp_admin_passwd=""
			log_echo "Passwords don't match."
		fi
	fi
	log_echo ""
done

#Set the postgres admin password
while [[ ! $set_postgres_admin_passwd =~ ^[YyNn]$ ]]; do
        read -p "Would you like to change the postgres user password (y/N)? " -n 1 set_postgres_admin_passwd
        if [[ $set_postgres_admin_passwd == "" ]]; then
                set_postgres_admin_passwd="n"
        fi
        log_echo ""
done
if [[ $set_postgres_admin_passwd =~ ^[Yy]$ ]]; then
	postgre_admin_passwd=""
	while [[ $postgres_admin_passwd == "" ]]; do
		read -p "Enter the postgres user password: " postgres_admin_passwd
		if [[ $postgres_admin_passwd == "" ]]; then
			log_echo "The password cannot be empty."
		else
			read -p "Enter the postgres user password again: " postgres_admin_passwd2
			log_echo ""
			if [[ $postgres_admin_passwd == $postgres_admin_passwd2 ]]; then
				log_echo "postgres user password set."
			else
				postgres_admin_passwd=""
				log_echo "Passwords don't match."
			fi
		fi
		log_echo ""
	done
fi

# Update pg_hba.conf
while [[ ! $update_pg_hba =~ ^[YyNn]$ ]]; do
        read -p "Would you like to update pg_hba.conf (Y/n)? " -n 1 update_pg_hba
        if [[ $update_pg_hba == "" ]]; then
                update_pg_hba="y"
        fi
        log_echo ""
done

# Add openerp postgres user
while [[ ! $create_pguser =~ ^[YyNn]$ ]]; do
	read -p "Would you like to add a postgresql openerp user (Y/n)? " -n 1 create_pguser
	if [[ $create_pguser == "" ]]; then
		create_pguser="y"
	fi
	log_echo ""
done

# Apache installation
while [[ ! $install_apache =~ ^[YyNn]$ ]]; do
	read -p "Would you like to install apache (Y/n)? " -n 1 install_apache
	if [[ $install_apache == "" ]]; then
		install_apache="y"
	fi
	log_echo ""
done

#Writting config file
#--------------------
mkdir -p /etc/openerp/$branch

echo "branch=$branch" > /etc/openerp/$branch/install.cfg
echo "server_type=$server_type" >> /etc/openerp/$branch/install.cfg
echo "openerp_user=$openerp_user" >> /etc/openerp/$branch/install.cfg
echo "install_openerp_addons=$install_openerp_addons" >> /etc/openerp/$branch/install.cfg
echo "install_ccorp_addons=$install_ccorp_addons" >> /etc/openerp/$branch/install.cfg
echo "install_costa_rica_addons=$install_costa_rica_addons" >> /etc/openerp/$branch/install.cfg
echo "install_extra_addons=$install_extra_addons" >> /etc/openerp/$branch/install.cfg
echo "install_magentoerpconnect=$install_magentoerpconnect" >> /etc/openerp/$branch/install.cfg
echo "install_nantic=$install_nantic" >> /etc/openerp/$branch/install.cfg

#Preparing installation
#----------------------
log_echo "Preparing installation"
log_echo "----------------------"
#Add openerp user
add_openerp_user
# Update the system.
update_system
# Install the required python libraries for openerp-server.
install_python_lib
# Install bazaar.
install_bzr
# Install postgresql
install_postgresql
# Update pg_hba.conf
if [[ $update_pg_hba =~ ^[Yy]$ ]]; then update_pg_hba; fi
# Add openerp postgres user
if [[ $create_pguser =~ ^[Yy]$ ]]; then add_postgres_user; fi
# Change postgres user password
if [[ $set_postgres_admin_passwd =~ ^[Yy]$ ]]; then change_postgres_passwd; fi

# Downloading OpenERP
#--------------------
log_echo "Downloading OpenERP"
log_echo "-------------------"
log_echo ""
download_openerp

# Install OpenERP
#----------------
log_echo "Installing OpenERP"
log_echo "------------------"
log_echo ""
install_openerp

# Install OpenERP Web Client
#---------------------------
log_echo "Installing OpenERP Web Client"
log_echo "-----------------------------"
log_echo ""
download_openerp_web
install_openerp_web_client

## Apache installation
install_apache

#~ Install phppgadmin
install_phppgadmin

#~ Make developer menus
make_menus

# Add log file rotation
add_log_rotation

exit 0
