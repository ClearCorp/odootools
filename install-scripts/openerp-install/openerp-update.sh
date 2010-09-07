#       openerp-update.sh
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
INSTALL_LOG_FILE=$INSTALL_LOG_PATH/update.log

if [[ ! -f $INSTALL_LOG_FILE ]]; then
	mkdir -p $INSTALL_LOG_PATH
	touch $INSTALL_LOG_FILE
fi

log ""

# Install logrotate
cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/logrotate.conf /etc/logrotate.d/openerp.conf

# Print title
log_echo "OpenERP update script"
log_echo "---------------------"
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
	install_path=$base_path/lib/$python_rel/dist-packages/openerp-server-skeleton
	install_path_web=$base_path/lib/$python_rel/dist-packages
	addons_path=$install_path/addons/
	sources_path=$base_path/src/openerp
else
	# Only Lucid supported for now
	log_echo "ERROR: This program must be executed on Ubuntu Lucid 10.04 (Desktop or Server)"
	exit 1
fi

# Check system values
if [[ ! check_system_values ]]; then
	exit 1
fi


# Initial questions
####################

#~ Detects server type
if [ ! -e /etc/openerp/type ]; then
	log_echo "Server type not found (/etc/openerp/type)"
	exit 1
else
	server_type=`cat /etc/openerp/type`
	if [[ ! $server_type =~ ^station|development|production$ ]]; then
		log_echo "Server type invalid (/etc/openerp/type): $server_type"
		exit 1
	fi
fi

#~ Detects server user
if [ ! -e /etc/openerp/user ]; then
	log_echo "Server user not found (/etc/openerp/user)"
	exit 1
else
	openerp_user=`cat /etc/openerp/user`
	if [[ ! `id $openerp_user` ]]; then
		log_echo "Server user invalid (/etc/openerp/user): $openerp_user"
		exit 1
	fi
fi

#~ Detects server branch
if [ ! -e /etc/openerp/branch ]; then
	log_echo "Server branch not found (/etc/openerp/branch)"
	exit 1
else
	branch=`cat /etc/openerp/branch`
	if [[ ! $branch =~ ^5[.]0|trunk$ ]]; then
		log_echo "Server branch invalid (/etc/openerp/branch): $branch"
		exit 1
	fi
fi

#~ Detects if extra-addons is installed
if [ ! -e /etc/openerp/extra_addons ]; then
	log_echo "Extra-addons installation file not found (/etc/openerp/extra_addons)"
	exit 1
else
	install_extra_addons=`cat /etc/openerp/extra_addons`
	if [[ ! $install_extra_addons =~ ^[YyNn]$ ]]; then
		log_echo "Extra-addons installation state invalid (/etc/openerp/extra_addons): $install_extra_addons"
		exit 1
	fi
fi

#~ Detects if magentoerpconnect is installed
if [ ! -e /etc/openerp/magentoerpconnect ]; then
	log_echo "magentoerpconnect installation file not found (/etc/openerp/magentoerpconnect)"
	exit 1
else
	install_magentoerpconnect=`cat /etc/openerp/magentoerpconnect`
	if [[ ! $install_magentoerpconnect =~ ^[YyNn]$ ]]; then
		log_echo "magentoerpconnect installation state invalid (/etc/openerp/magentoerpconnect): $install_magentoerpconnect"
		exit 1
	fi
fi

#~ Detects if nantic is installed
if [ ! -e /etc/openerp/nantic ]; then
	log_echo "nantic installation file not found (/etc/openerp/nantic)"
	exit 1
else
	install_nantic=`cat /etc/openerp/nantic`
	if [[ ! $install_nantic =~ ^[YyNn]$ ]]; then
		log_echo "nantic installation state invalid (/etc/openerp/nantic): $install_nantic"
		exit 1
	fi
fi

#Preparing update
#----------------
log_echo "Preparing update"
log_echo "----------------"
# Updating user
add_openerp_user
# Update the system.
update_system
# Updating the required python libraries for openerp-server.
install_python_lib
# Updating bazaar.
install_bzr
# Updating postgresql
install_postgresql

# Downloading OpenERP
#--------------------
log_echo "Downloading OpenERP"
log_echo "-------------------"
log_echo ""
download_openerp


# Updating OpenERP
#################

log_echo "Updating OpenERP"
log_echo "----------------"
log_echo ""

#~ Make skeleton installation
if [ -e $install_path ]; then
	tar cvfz $sources_path/openerp-server-skeleton-backup-`date +%Y-%m-%d_%H-%M-%S`.tgz $install_path >> $INSTALL_LOG_FILE
	rm -r $install_path >> $INSTALL_LOG_FILE
fi

install_openerp

# Updating OpenERP Web Client
#----------------------------
log_echo "Updating OpenERP Web Client"
log_echo "---------------------------"
log_echo ""
install_openerp_web_client

# Add log file rotation
add_log_rotation

exit 0
