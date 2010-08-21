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
	log_echo ""
	log_echo "Finished ccorp-ubuntu-server-install"
	log_echo "Continuing ccorp-openerp-install..."
	log_echo ""
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
mkdir -p /etc/openerp
if [[ $server_type =~ ^[Ww]$ ]]; then
	log_echo "This is a working station"
	echo "station" > /etc/openerp/type
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
	mkdir -p /etc/openerp
	if [[ $server_type =~ ^[Pp]$ ]]; then
		log_echo "This is a production server"
		echo "production" > /etc/openerp/type
		branch="s"
		install_extra_addons="n"
		install_magentoerpconnect="n"
		install_nantic="n"
	else
		echo "development" > /etc/openerp/type
	fi
	openerp_user="openerp"
fi
echo $openerp_user > /etc/openerp/user

#Choose the branch to install
while [[ ! $branch =~ ^[SsTt]$ ]]; do
	read -p "Which branch do you want to install (Stable/trunk)? " -n 1 branch
	if [[ $branch == "" ]]; then
		branch="s"
	fi
	log_echo ""
done
if [[ $branch =~ ^[Ss]$ ]]; then
	log_echo "This installation will use stable branch."
	branch="5.0"
else
	log_echo "This installation will use trunk branch."
	branch="trunk"
fi
echo $branch > /etc/openerp/branch
echo ""

#Install extra-addons
while [[ ! $install_extra_addons =~ ^[YyNn]$ ]]; do
        read -p "Would you like to install extra addons (Y/n)? " -n 1 install_extra_addons
        if [[ $install_extra_addons == "" ]]; then
                install_extra_addons="y"
        fi
        log_echo ""
done
echo $install_extra_addons > /etc/openerp/extra_addons

#Install magentoerpconnect
while [[ ! $install_magentoerpconnect =~ ^[YyNn]$ ]]; do
        read -p "Would you like to install magentoerpconnect (Y/n)? " -n 1 install_magentoerpconnect
        if [[ $install_magentoerpconnect == "" ]]; then
                install_magentoerpconnect="y"
        fi
        log_echo ""
done
echo $install_magentoerpconnect > /etc/openerp/magentoerpconnect

#Install nan-tic modules
while [[ ! $install_nantic =~ ^[YyNn]$ ]]; do
        read -p "Would you like to install nan-tic modules (Y/n)? " -n 1 install_nantic
        if [[ $install_nantic == "" ]]; then
                install_nantic="y"
        fi
        log_echo ""
done
echo $install_nantic > /etc/openerp/nantic

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

#Preparing installation
#######################

log_echo "Preparing installation"
log_echo "----------------------"

#Add openerp user
log_echo "Adding openerp user..."
adduser --system --home /var/run/openerp --no-create-home --group openerp >> $INSTALL_LOG_FILE
if [[ $server_type =~ ^[Ww]$ ]]; then
	adduser $openerp_user openerp
fi
openerp_user="openerp"
log_echo ""

# Update the system.
log_echo "Updating the system..."
apt-get -qq update >> $INSTALL_LOG_FILE
apt-get -qqy upgrade >> $INSTALL_LOG_FILE
log_echo ""

# Install the required python libraries for openerp-server.
echo "Installing the required python libraries for openerp-server..."
apt-get -qqy install python python-psycopg2 python-reportlab python-egenix-mxdatetime python-tz python-pychart python-pydot python-lxml python-libxslt1 python-vobject python-imaging python-yaml >> $INSTALL_LOG_FILE
apt-get -qqy install python python-dev build-essential python-setuptools python-profiler python-simplejson >> $INSTALL_LOG_FILE
apt-get -qqy install python-xlwt >> $INSTALL_LOG_FILE
apt-get -qqy install postgresql-plpython-8.4 python-qt4 python-dbus python-qt4-dbus pyro >> $INSTALL_LOG_FILE
log_echo ""

# Install bazaar.
log_echo "Installing bazaar..."
apt-get -qqy install bzr >> $INSTALL_LOG_FILE
bzr whoami "ClearCorp S.A. <info@clearcorp.co.cr>" >> $INSTALL_LOG_FILE
log_echo ""

# Install postgresql
log_echo "Installing postgresql..."
apt-get -qqy install postgresql >> $INSTALL_LOG_FILE
log_echo ""

log_echo ""
# Update pg_hba.conf
if [[ $update_pg_hba =~ ^[Yy]$ ]]; then
	sed -i 's/\(local[[:space:]]*all[[:space:]]*all[[:space:]]*\)\(ident[[:space:]]*sameuser\)/\1md5/g' /etc/postgresql/$posgresql_rel/main/pg_hba.conf >> $INSTALL_LOG_FILE
	/etc/init.d/postgresql-$posgresql_rel restart >> $INSTALL_LOG_FILE
fi

# Add openerp postgres user
if [[ $create_pguser =~ ^[Yy]$ ]]; then
	/usr/bin/sudo -u postgres createuser $openerp_user --superuser --createdb --no-createrole >> $INSTALL_LOG_FILE
	/usr/bin/sudo -u postgres psql template1 -U postgres -c "alter user $openerp_user with password '$openerp_admin_passwd'" >> $INSTALL_LOG_FILE
	log_echo ""
fi

# Change postgres user password
if [[ $set_postgres_admin_passwd =~ ^[Yy]$ ]]; then
	log_echo "Changing postgres user password on request..."
	log_echo "postgres:$postgres_admin_passwd" | chpasswd
	sudo -u postgres psql template1 -U postgres -c "alter user postgres with password '$postgres_admin_passwd'" >> $INSTALL_LOG_FILE
	log_echo ""
fi


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

# Download openerp ccorp-addons latest stable/trunk branch.
log_echo "Downloading openerp ccorp-addons latest stable/trunk branch..."
if [ -e ccorp-addons ]; then
	bzr update ccorp-addons >> $INSTALL_LOG_FILE
else
	bzr checkout --lightweight lp:openerp-ccorp-addons ccorp-addons >> $INSTALL_LOG_FILE
fi
log_echo ""

# Download openerp-costa-rica latest stable/trunk branch.
log_echo "Downloading openerp-costa-rica latest stable/trunk branch..."
if [ -e costa-rica ]; then
	bzr update costa-rica >> $INSTALL_LOG_FILE
else
	bzr checkout --lightweight lp:openerp-costa-rica costa-rica >> $INSTALL_LOG_FILE
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
	log_echo "Removing use_control from extra addons..."
	rm -r extra-addons/use_control >> $INSTALL_LOG_FILE
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


# Install OpenERP
#################

log_echo "Installing OpenERP"
log_echo "------------------"
log_echo ""

cd $sources_path

# Install OpenERP server
log_echo "Installing OpenERP Server..."
cd openerp-server >> $INSTALL_LOG_FILE

#~ Make skeleton installation
mkdir -p $install_path >> $INSTALL_LOG_FILE
cp -a bin/* $install_path/ >> $INSTALL_LOG_FILE

#~ Copy documentation
mkdir -p $base_path/share/doc/openerp-server >> $INSTALL_LOG_FILE
cp -a doc/* $base_path/share/doc/openerp-server/ >> $INSTALL_LOG_FILE

#~ Install man pages
mkdir -p $base_path/share/man/man1 >> $INSTALL_LOG_FILE
mkdir -p $base_path/share/man/man5 >> $INSTALL_LOG_FILE
cp -a man/*.1 $base_path/share/man/man1/ >> $INSTALL_LOG_FILE
cp -a man/*.5 $base_path/share/man/man5/ >> $INSTALL_LOG_FILE

#~ Copy bin script skeleton to etc
mkdir -p /etc/openerp/server/ >> $INSTALL_LOG_FILE
cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/server-bin-skeleton /etc/openerp/server/bin-skeleton >> $INSTALL_LOG_FILE

# Change permissions
chown -R $openerp_user:$openerp_user $install_path >> $INSTALL_LOG_FILE
chmod 755 $addons_path >> $INSTALL_LOG_FILE

# Add filestore dir and change permissions
mkdir -p $install_path/filestore >> $INSTALL_LOG_FILE
chown -R $openerp_user:$opnerp_user $install_path/filestore >> $INSTALL_LOG_FILE

# OpenERP Server init and config skeletons
cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/server-init-skeleton /etc/openerp/server/init-skeleton >> $INSTALL_LOG_FILE
sed -i "s#\\[PATH\\]#$base_path#g" /etc/openerp/server/init-skeleton >> $INSTALL_LOG_FILE
cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/server.conf-skeleton /etc/openerp/server/ >> $INSTALL_LOG_FILE
if [[ $server_type =~ ^[Pp]$ ]]; then
	sed -i "s#\\[LOGLEVEL\\]#info#g" /etc/openerp/server/server.conf-skeleton >> $INSTALL_LOG_FILE
else
	sed -i "s#\\[LOGLEVEL\\]#debug#g" /etc/openerp/server/server.conf-skeleton >> $INSTALL_LOG_FILE
fi

# Install OpenERP addons
log_echo "Installing OpenERP addons..."
mkdir -p $addons_path >> $INSTALL_LOG_FILE
cd $sources_path >> $INSTALL_LOG_FILE
cp -a addons/* $addons_path >> $INSTALL_LOG_FILE

# Install OpenERP ccorp-addons
log_echo "Installing OpenERP ccorp-addons..."
cp -a ccorp-addons/* $addons_path >> $INSTALL_LOG_FILE

# Install OpenERP costa-rica
log_echo "Installing OpenERP costa-rica..."
cp -a costa-rica/* $addons_path >> $INSTALL_LOG_FILE

# Install OpenERP extra addons
if [[ "$install_extra_addons" =~ ^[Yy]$ ]]; then
	log_echo "Installing OpenERP extra addons..."
	cp -a extra-addons/* $addons_path >> $INSTALL_LOG_FILE
fi

# Install OpenERP magentoerpconnect
if [[ "$install_magentoerpconnect" =~ ^[Yy]$ ]]; then
	log_echo "Installing OpenERP magentoerpconnect..."
	cp -a magentoerpconnect $addons_path >> $INSTALL_LOG_FILE
fi

# Install nan-tic modules
if [[ "$install_nantic" =~ ^[Yy]$ ]]; then
	log_echo "Installing nan-tic modules..."
	rm openobject-client-kde/server-modules/*.sh >> $INSTALL_LOG_FILE
	cp -a openobject-client-kde/server-modules/* $addons_path >> $INSTALL_LOG_FILE
fi

#~ Make pid dir
mkdir -p /var/run/openerp >> $INSTALL_LOG_FILE
chown $openerp_user:root /var/run/openerp >> $INSTALL_LOG_FILE
sed -i "s#exit 0#mkdir -p /var/run/openerp\\\\nchown $openerp_user:root /var/run/openerp\\\\n#g" /etc/rc.local >> $INSTALL_LOG_FILE

cd $sources_path >> $INSTALL_LOG_FILE

# Install OpenERP Web client
log_echo "Installing OpenERP Web client..."
easy_install -U openerp-web >> $INSTALL_LOG_FILE

# OpenERP Web Client init and config skeletons
mkdir -p /etc/openerp/web-client >> $INSTALL_LOG_FILE
cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/web-client-init-skeleton /etc/openerp/web-client/init-skeleton >> $INSTALL_LOG_FILE
sed -i "s#\\[PATH\\]#$base_path#g" /etc/openerp/web-client/init-skeleton >> $INSTALL_LOG_FILE
sed -i "s#\\[USER\\]#$openerp_user#g" /etc/openerp/web-client/init-skeleton >> $INSTALL_LOG_FILE
cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/web-client.conf-skeleton /etc/openerp/web-client/ >> $INSTALL_LOG_FILE

#~ Sets server type
if [[ "$server_type" =~ ^[DdWw]$ ]]; then
	sed -i "s/\[TYPE\]/development/g" /etc/openerp/web-client/web-client.conf-skeleton >> $INSTALL_LOG_FILE
else
	sed -i "s/\[TYPE\]/production/g" /etc/openerp/web-client/web-client.conf-skeleton >> $INSTALL_LOG_FILE
fi

#~ Adds ClearCorp logo
for i in `ls -d $install_path_web/openerp_web*`; do
	ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-install/company_logo.png $i/openerp/static/images/company_logo.png >> $INSTALL_LOG_FILE
done

#~ Adds ClearCorp favicon
for i in `ls -d $install_path_web/openerp_web*`; do
	ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-install/favicon.ico $i/openerp/static/images/favicon.ico >> $INSTALL_LOG_FILE
done

#~ Adds bin symlink
ln -s $install_path_web/openerp-web $base_path/bin/openerp-web >> $INSTALL_LOG_FILE

## Apache installation

if [[ "$install_apache" =~ ^[Yy]$ ]]; then
	log_echo "Installing Apache..."
	apt-get -qqy install apache2 >> $INSTALL_LOG_FILE

	log_echo "Making SSL certificate for Apache...";
	make-ssl-cert generate-default-snakeoil --force-overwrite >> $INSTALL_LOG_FILE
	# Snakeoil certificate files:
	# /usr/share/ssl-cert/ssleay.cnf
	# /etc/ssl/certs/ssl-cert-snakeoil.pem
	# /etc/ssl/private/ssl-cert-snakeoil.key

	log_echo "Enabling Apache Modules..."
	# Apache Modules:
	a2enmod ssl >> $INSTALL_LOG_FILE
	a2enmod rewrite >> $INSTALL_LOG_FILE
	a2enmod suexec >> $INSTALL_LOG_FILE
	a2enmod include >> $INSTALL_LOG_FILE
	a2enmod proxy >> $INSTALL_LOG_FILE
	a2enmod proxy_http >> $INSTALL_LOG_FILE
	a2enmod proxy_connect >> $INSTALL_LOG_FILE
	a2enmod proxy_ftp >> $INSTALL_LOG_FILE
	a2enmod headers >> $INSTALL_LOG_FILE
	a2ensite default >> $INSTALL_LOG_FILE
	a2ensite default-ssl >> $INSTALL_LOG_FILE

	log_echo "Configuring site config files..."
	cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/apache-erp /etc/apache2/sites-available/erp >> $INSTALL_LOG_FILE
	mkdir -p /etc/openerp/apache2/rewrites >> $INSTALL_LOG_FILE
	cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/apache-ssl-skeleton /etc/openerp/apache2/ssl-skeleton >> $INSTALL_LOG_FILE
	sed -i "s/ServerAdmin webmaster@localhost/ServerAdmin support@clearnet.co.cr\n\n\tInclude \/etc\/apache2\/sites-available\/erp/g" /etc/apache2/sites-available/default >> $INSTALL_LOG_FILE
	sed -i "s/ServerAdmin webmaster@localhost/ServerAdmin support@clearnet.co.cr\n\n\tInclude \/etc\/openerp\/apache2\/rewrites/g" /etc/apache2/sites-available/default-ssl >> $INSTALL_LOG_FILE


	log_echo "Restarting Apache..."
	/etc/init.d/apache2 restart >> $INSTALL_LOG_FILE
fi

#~ TODO: Add shorewall support in ubuntu-server-install, and add rules here

#~ Install phppgadmin
log_echo "Installing PostgreSQL Web administration interface (phppgadmin)..."
apt-get -qy install phppgadmin >> $INSTALL_LOG_FILE
sed -i "s/#\?[[:space:]]*\(deny from all.*\)/# deny from all/g" /etc/phppgadmin/apache.conf >> $INSTALL_LOG_FILE
sed -i "s/[[:space:]]*allow from \(.*\)/# allow from \1/g" /etc/phppgadmin/apache.conf >> $INSTALL_LOG_FILE
sed -i "s/#\?[[:space:]]*\(allow from all.*\)/allow from all/g" /etc/phppgadmin/apache.conf >> $INSTALL_LOG_FILE
sed -i "s/#\?[[:space:]]*\(allow from all.*\)/allow from all/g" /etc/phppgadmin/apache.conf >> $INSTALL_LOG_FILE
/etc/init.d/apache2 restart >> $INSTALL_LOG_FILE

#~ Make developer menus
if [[ $type == "station" ]]; then
	sudo -u $openerp_user $LIBBASH_CCORP_DIR/install-scripts/openerp-install/mkmenus-ccorp-main.sh
fi
exit 0
