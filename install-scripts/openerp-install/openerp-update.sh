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
. $LIBBASH_CCORP_DIR/main-lib/installFonts.sh

# Check user is root
checkRoot

# Init log file
INSTALL_LOG_PATH=/var/log/openerp
INSTALL_LOG_FILE=$INSTALL_LOG_PATH/update.log

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

# Run the Ubuntu preparation script.
while [[ ! $run_preparation_script =~ ^[YyNn]$ ]]; do
	read -p "Do you want to run ccorp-ubuntu-server-update script (recommended if not already done) (y/N)? " -n 1 run_preparation_script
	if [[ $run_preparation_script == "" ]]; then
		run_preparation_script="n"
	fi
	log_echo ""
done
if [[ $run_preparation_script =~ ^[Yy]$ ]]; then
	log_echo "Running ccorp-ubuntu-server-install..."
	log_echo ""
	ccorp-ubuntu-server-install
	log_echo ""
	log_echo "Finished ccorp-ubuntu-server-install"
	log_echo "Continuing ccorp-openerp-update..."
	log_echo ""
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
#######################

log_echo "Preparing update"
log_echo "----------------"

# Update the system.
log_echo "Updating the system..."
apt-get -qq update >> $INSTALL_LOG_FILE
apt-get -qqy upgrade >> $INSTALL_LOG_FILE
log_echo ""

# Updating the required python libraries for openerp-server.
echo "Updating the required python libraries for openerp-server..."
apt-get -qqy install python python-psycopg2 python-reportlab python-egenix-mxdatetime python-tz python-pychart python-pydot python-lxml python-libxslt1 python-vobject python-imaging python-yaml >> $INSTALL_LOG_FILE
apt-get -qqy install python python-dev build-essential python-setuptools python-profiler python-simplejson >> $INSTALL_LOG_FILE
apt-get -qqy install python-xlwt >> $INSTALL_LOG_FILE
apt-get -qqy install pyro >> $INSTALL_LOG_FILE
log_echo ""

# Updating bazaar.
log_echo "Updating bazaar..."
apt-get -qqy install bzr >> $INSTALL_LOG_FILE
bzr whoami "ClearCorp S.A. <info@clearcorp.co.cr>" >> $INSTALL_LOG_FILE
log_echo ""

# Updating postgresql
log_echo "Updating postgresql..."
apt-get -qqy install postgresql >> $INSTALL_LOG_FILE
log_echo ""


# Downloading OpenERP
#####################

log_echo "Downloading OpenERP"
log_echo "-------------------"
log_echo ""

mkdir -p $sources_path >> $INSTALL_LOG_FILE
cd $sources_path >> $INSTALL_LOG_FILE

# Download openerp-server latest stable/trunk release.
log_echo "Downloading openerp-server latest stable/trunk release..."
if [ -e openerp-server ]; then
	bzr update openerp-server >> $INSTALL_LOG_FILE
else
	bzr checkout --lightweight lp:openobject-server/$branch openerp-server >> $INSTALL_LOG_FILE
fi
log_echo ""

# Download openerp addons latest stable/trunk branch.
log_echo "Downloading openerp addons latest stable/trunk branch..."
if [ -e addons ]; then
	bzr update addons >> $INSTALL_LOG_FILE
else
	bzr checkout --lightweight lp:openobject-addons/$branch addons >> $INSTALL_LOG_FILE
fi
log_echo ""

# Download extra addons
if [[ $install_extra_addons =~ ^[Yy]$ ]]; then
	log_echo "Downloading extra addons..."
	if [ -e extra-addons ]; then
		bzr update extra-addons >> $INSTALL_LOG_FILE
	else
		bzr checkout --lightweight lp:openobject-addons/extra-$branch extra-addons >> $INSTALL_LOG_FILE
	fi
	log_echo ""
fi

# Download magentoerpconnect
if [[ $install_magentoerpconnect =~ ^[Yy]$ ]]; then
	log_echo "Downloading magentoerpconnect..."
	if [ -e magentoerpconnect ]; then
		bzr update magentoerpconnect >> $INSTALL_LOG_FILE
	else
		bzr checkout --lightweight lp:magentoerpconnect magentoerpconnect >> $INSTALL_LOG_FILE
	fi
	log_echo ""
fi

# Download nan-tic modules
if [[ $install_nantic =~ ^[Yy]$ ]]; then
	log_echo "Downloading nan-tic modules..."
	if [ -e openobject-client-kde ]; then
		bzr update openobject-client-kde >> $INSTALL_LOG_FILE
	else
		bzr checkout --lightweight lp:~openobject-client-kde/openobject-client-kde/$branch openobject-client-kde >> $INSTALL_LOG_FILE
	fi
	log_echo ""
fi


# Updating OpenERP
#################

log_echo "Updating OpenERP"
log_echo "----------------"
log_echo ""

cd $sources_path >> $INSTALL_LOG_FILE

# Updating OpenERP server
log_echo "Updating OpenERP Server..."
cd openerp-server >> $INSTALL_LOG_FILE

#~ Make skeleton installation
if [ -e $install_path ]; then
	tar cvfz $sources_path/openerp-server-skeleton-backup-`date +%Y-%m-%d_%H-%M-%S`.tgz $install_path >> $INSTALL_LOG_FILE
	rm -r $install_path >> $INSTALL_LOG_FILE
fi
mkdir -p $install_path >> $INSTALL_LOG_FILE
cp -a bin/* $install_path/ >> $INSTALL_LOG_FILE

# Making ClearCorp fonts available to ReportLab
installFonts
cp -a $LIBBASH_CCORP_DIR/install-scripts/openerp-install/ccorp-fonts.py $install_path/report/render/rml2pdf/ >> $INSTALL_LOG_FILE
echo "import ccorp-fonts" >> $install_path/report/render/rml2pdf/__init__.py

#~ Copy documentation
mkdir -p $base_path/share/doc/openerp-server >> $INSTALL_LOG_FILE
cp -a doc/* $base_path/share/doc/openerp-server/ >> $INSTALL_LOG_FILE

#~ Install man pages
mkdir -p $base_path/share/man/man1 >> $INSTALL_LOG_FILE
mkdir -p $base_path/share/man/man5 >> $INSTALL_LOG_FILE
cp -a man/*.1 $base_path/share/man/man1/ >> $INSTALL_LOG_FILE
cp -a man/*.5 $base_path/share/man/man5/ >> $INSTALL_LOG_FILE

# Change permissions
chown -R $opnerp_user:root $install_path >> $INSTALL_LOG_FILE
chmod 755 $addons_path >> $INSTALL_LOG_FILE

# Add filestore dir and change permissions
mkdir -p $install_path/filestore >> $INSTALL_LOG_FILE
chown -R $opnerp_user:root $install_path/filestore >> $INSTALL_LOG_FILE

# Updating OpenERP addons
log_echo "Updating OpenERP addons..."
mkdir -p $addons_path >> $INSTALL_LOG_FILE
cd $sources_path >> $INSTALL_LOG_FILE
cp -a addons/* $addons_path >> $INSTALL_LOG_FILE

# Updating OpenERP extra addons
if [[ "$install_extra_addons" =~ ^[Yy]$ ]]; then
	log_echo "Updating OpenERP extra addons..."
	cp -a extra-addons/* $addons_path >> $INSTALL_LOG_FILE
fi

# Updating OpenERP magentoerpconnect
if [[ "$install_magentoerpconnect" =~ ^[Yy]$ ]]; then
	log_echo "Updating OpenERP magentoerpconnect..."
	cp -a magentoerpconnect $addons_path >> $INSTALL_LOG_FILE
fi

# Updating nan-tic modules
if [[ "$install_nantic" =~ ^[Yy]$ ]]; then
	log_echo "Updating nan-tic modules..."
	rm openobject-client-kde/server-modules/*.sh >> $INSTALL_LOG_FILE
	cp -a openobject-client-kde/server-modules/* $addons_path >> $INSTALL_LOG_FILE
fi

cd $sources_path >> $INSTALL_LOG_FILE

# Updating OpenERP Web client
log_echo "Updating OpenERP Web client..."
easy_install -U openerp-web >> $INSTALL_LOG_FILE >> $INSTALL_LOG_FILE

#~ Adds ClearCorp logo
for i in `ls -d $install_path_web/openerp_web*`; do
	ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-install/company_logo.png $i/openerp/static/images/company_logo.png >> $INSTALL_LOG_FILE
done

#~ Adds bin symlink
ln -s $install_path_web/openerp-web $base_path/bin/openerp-web >> $INSTALL_LOG_FILE

exit 0
