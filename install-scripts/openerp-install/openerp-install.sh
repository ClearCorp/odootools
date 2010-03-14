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

# Print title
echo "OpenERP installation script"
echo "---------------------------"
echo ""

# Set distribution
dist=""
getDist dist
echo "Distribution: $dist"
echo ""

# Sets vars corresponding to the distro
if [[ $dist == "karmic" ]]; then
	# Ubuntu 9.10, python 2.6
	posgresql_rel=8.4
	python_rel=python2.6
	ubuntu_rel=9.10
	base_path=/usr/local
	install_path=$base_path/lib/$python_rel/dist-packages/openerp-server-skeleton
	install_path_web=$base_path/lib/$python_rel/dist-packages
	addons_path=$install_path/addons/
	sources_path=$base_path/src
else
	# Only Karmic supported for now
	echo "This program must be executed on Ubuntu Karmic 9.10 (Desktop or Server)"
	exit 1
fi

# Run the Ubuntu preparation script.
while [[ ! $run_preparation_script =~ ^[YyNn]$ ]]; do
	read -p "Do you want to run ccorp-ubuntu-server-install script (recommended if not already done) (y/N)? " -n 1 run_preparation_script
	if [[ $run_preparation_script == "" ]]; then
		run_preparation_script="n"
	fi
	echo ""
done
if [[ $run_preparation_script =~ ^[Yy]$ ]]; then
	echo ""
	ccorp-ubuntu-server-install
fi


# Initial questions
####################

#~ Choose between development and production server
while [[ ! $server_type =~ ^[DdPp]$ ]]; do
	read -p "Is this a development or production server (D/p)? " -n 1 server_type
	if [[ $server_type == "" ]]; then
		server_type="d"
	fi
	echo ""
done
if [[ $server_type =~ ^[Pp]$ ]]; then
	echo "This is a production server"
	branch="s"
	install_extra_addons="n"
	install_magentoerpconnect="n"
fi

#Choose the branch to install
while [[ ! $branch =~ ^[SsTt]$ ]]; do
	read -p "Which branch do you want to install (Stable/trunk)? " -n 1 branch
	if [[ $branch == "" ]]; then
		branch="s"
	fi
	echo ""
done
if [[ $branch =~ ^[Ss]$ ]]; then
	echo "This installation will use stable branch."
	branch="5.0"
else
	echo "This installation will use trunk branch."
	branch="trunk"
fi
echo ""

#Install extra-addons
while [[ ! $install_extra_addons =~ ^[YyNn]$ ]]; do
        read -p "Would you like to install extra addons (Y/n)? " -n 1 install_extra_addons
        if [[ $install_extra_addons == "" ]]; then
                install_extra_addons="y"
        fi
        echo ""
done

#Install magentoerpconnect
while [[ ! $install_magentoerpconnect =~ ^[YyNn]$ ]]; do
        read -p "Would you like to install magentoerpconnect (Y/n)? " -n 1 install_magentoerpconnect
        if [[ $install_magentoerpconnect == "" ]]; then
                install_magentoerpconnect="y"
        fi
        echo ""
done

#Select FQDN
fqdn=""
while [[ $fqdn == "" ]]; do
        read -p "Enter the FQDN for this server (`cat /etc/hostname`)? " fqdn
        if [[ $fqdn == "" ]]; then
                fqdn=`cat /etc/hostname`
        fi
        echo ""
done

#Set the openerp admin password
openerp_admin_passwd=""
while [[ $openerp_admin_passwd == "" ]]; do
	read -p "Enter the OpenERP administrator password: " openerp_admin_passwd
	if [[ $openerp_admin_passwd == "" ]]; then
		echo "The password cannot be empty."
	else
		read -p "Enter the OpenERP administrator password again: " openerp_admin_passwd2
		echo ""
		if [[ $openerp_admin_passwd == $openerp_admin_passwd2 ]]; then
			echo "OpenERP administrator password set."
		else
			openerp_admin_passwd=""
			echo "Passwords don't match."
		fi
	fi
	echo ""
done

#Set the postgres admin password
while [[ ! $set_postgres_admin_passwd =~ ^[YyNn]$ ]]; do
        read -p "Would you like to change the postgres user password (Y/n)? " -n 1 set_postgres_admin_passwd
        if [[ $set_postgres_admin_passwd == "" ]]; then
                set_postgres_admin_passwd="y"
        fi
        echo ""
done
if [[ $set_postgres_admin_passwd =~ ^[Yy]$ ]]; then
	postgre_admin_passwd=""
	while [[ $postgres_admin_passwd == "" ]]; do
		read -p "Enter the postgres user password: " postgres_admin_passwd
		if [[ $postgres_admin_passwd == "" ]]; then
			echo "The password cannot be empty."
		else
			read -p "Enter the postgres user password again: " postgres_admin_passwd2
			echo ""
			if [[ $postgres_admin_passwd == $postgres_admin_passwd2 ]]; then
				echo "postgres user password set."
			else
				postgres_admin_passwd=""
				echo "Passwords don't match."
			fi
		fi
		echo ""
	done
fi

#Preparing installation
#######################

echo "Preparing installation"
echo "----------------------"

#Add openerp user
echo "Adding openerp user..."
adduser --quiet --system openerp
echo ""

# Update the system.
echo "Updating the system..."
apt-get -qq update
apt-get -qqy upgrade
echo ""

# Install the required python libraries for openerp-server.
echo "Installing the required python libraries for openerp-server..."
apt-get -qqy install python python-psycopg2 python-reportlab python-egenix-mxdatetime python-tz python-pychart python-pydot python-lxml python-libxslt1 python-vobject python-imaging python-dev build-essential python-setuptools python-profiler
echo ""

# Install bazaar.
echo "Installing bazaar..."
apt-get -qqy install bzr
bzr whoami "ClearCorp S.A. <info@clearcorp.co.cr>"
echo ""

# Install postgresql
echo "Installing postgresql."
apt-get -qqy install postgresql
echo ""

echo ""
# Update pg_hba.conf
while [[ ! $update_pg_hba =~ ^[YyNn]$ ]]; do
        read -p "Would you like to update pg_hba.conf (Y/n)? " -n 1 update_pg_hba
        if [[ $update_pg_hba == "" ]]; then
                update_pg_hba="y"
        fi
        echo ""
done
if [[ $update_pg_hba =~ ^[Yy]$ ]]; then
	sed -i 's/\(local[[:space:]]*all[[:space:]]*all[[:space:]]*\)\(ident[[:space:]]*sameuser\)/\1md5/g' /etc/postgresql/$posgresql_rel/main/pg_hba.conf
	/etc/init.d/postgresql-$posgresql_rel restart
fi

# Add openerp postgres user
while [[ ! $create_pguser =~ ^[YyNn]$ ]]; do
        read -p "Would you like to add a postgresql openerp user (Y/n)? " -n 1 create_pguser
        if [[ $create_pguser == "" ]]; then
                create_pguser="y"
        fi
        echo ""
done
if [[ $create_pguser =~ ^[Yy]$ ]]; then
	sudo -u postgres createuser openerp --no-superuser --createdb --no-createrole
	sudo -u postgres psql template1 -U postgres -c "alter user openerp with password '$openerp_admin_passwd'"
fi

# Change postgres user password
echo "Changing postgres user password on request..."
if [[ $set_postgres_admin_passwd =~ ^[Yy]$ ]]; then
	echo "postgres:$postgres_admin_passwd" | chpasswd
	sudo -u postgres psql template1 -U postgres -c "alter user postgres with password '$postgres_admin_passwd'"
fi


# Downloading OpenERP
#####################

echo "Downloading OpenERP"
echo "-------------------"
echo ""

cd $sources_path

# Download openerp-server latest stable/trunk release.
echo "Downloading openerp-server latest stable/trunk release..."
bzr checkout --lightweight lp:openobject-server/$branch openerp-server
echo ""

# Download openerp addons latest stable/trunk branch.
echo "Downloading openerp addons latest stable/trunk branch..."
bzr checkout --lightweight lp:openobject-addons/$branch addons
echo ""

# Download extra addons
if [[ $install_extra_addons =~ ^[Yy]$ ]]; then
	echo "Downloading extra addons..."
	bzr checkout --lightweight lp:openobject-addons/extra-$branch extra-addons
	echo ""
fi

# Download magentoerpconnect
if [[ $install_magentoerpconnect =~ ^[Yy]$ ]]; then
	echo "Downloading magentoerpconnect..."
	bzr checkout --lightweight lp:magentoerpconnect magentoerpconnect
	echo ""
fi


# Install OpenERP
#################

echo "Installing OpenERP"
echo "------------------"
echo ""

cd $sources_path

# Install OpenERP server
echo "Installing OpenERP Server..."
cd openerp-server

#~ Make skeleton installation
mkdir -p $install_path
cp -a bin/* $install_path/

#~ Copy documentation
mkdir -p $base_path/share/doc/openerp-server
cp -a doc/* $base_path/share/doc/openerp-server/

#~ Install man pages
mkdir -p $base_path/share/man/man1
mkdir -p $base_path/share/man/man5
cp -a man/*.1 $base_path/share/man/man1/
cp -a man/*.5 $base_path/share/man/man5/

#~ Copy bin script skeleton to etc
mkdir -p /etc/openerp/server/
cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/server-bin-skeleton /etc/openerp/server/bin-skeleton

# Change permissions
chown -R openerp:root $install_path
chmod 755 $addons_path

# OpenERP Server init and config skeletons
cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/server-init-skeleton /etc/openerp/server/init-skeleton
sed -i "s/\[PATH\]/$base_path/g" /etc/openerp/server/init-skeleton
cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/server.conf-skeleton /etc/openerp/server/

# Install OpenERP addons
echo "Installing OpenERP addons..."
mkdir -p $addons_path
cd $sources_path
cp -a addons/* $addons_path

# Install OpenERP extra addons
if [[ "$install_extra_addons" =~ ^[Yy]$ ]]; then
	echo "Installing OpenERP extra addons..."
	cp -a extra-addons/* $addons_path
fi

# Install OpenERP magentoerpconnect
if [[ "$install_magentoerpconnect" =~ ^[Yy]$ ]]; then
	echo "Installing OpenERP magentoerpconnect..."
	cp -a magentoerpconnect $addons_path
fi

cd $sources_path


# Install OpenERP Web client
echo "Installing OpenERP Web client..."
easy_install -U -d $install_path_web openerp-web
ln -s $install_path_web/openerp_web* $install_path_web/openerp-web

# OpenERP Web Client init and config skeletons
mkdir -p /etc/openerp/web-client
cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/web-client-init-skeleton /etc/openerp/web-client/init-skeleton
sed -i "s/\[PATH\]/${base_path}/g" /etc/openerp/web-client/init-skeleton
cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/web-client.conf-skeleton /etc/openerp/web-client/

#~ Sets server type
if [[ "$server_type" =~ ^[Dd]$ ]]; then
	sed -i "s/\[TYPE\]/development/g" /etc/openerp/web-client/init-skeleton
elif
	sed -i "s/\[TYPE\]/production/g" /etc/openerp/web-client/init-skeleton
fi

#~ Adds ClearCorp logo
ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-install/company_logo.png $install_path_web/openerp-web-skeleton/openerp/static/images/company_logo.png


## Apache installation
while [[ ! $install_apache =~ ^[YyNn]$ ]]; do
	read -p "Would you like to install apache (Y/n)? " -n 1 install_apache
	if [[ $install_apache == "" ]]; then
		install_apache="y"
	fi
	echo ""
done

if [[ "$install_apache" =~ ^[Yy]$ ]]; then
	echo "Installing Apache..."
	apt-get -qy install apache2

	echo "Making SSL certificate for Apache...";
	make-ssl-cert generate-default-snakeoil --force-overwrite
	# Snakeoil certificate files:
	# /usr/share/ssl-cert/ssleay.cnf
	# /etc/ssl/certs/ssl-cert-snakeoil.pem
	# /etc/ssl/private/ssl-cert-snakeoil.key

	echo "Enabling Apache Modules..."
	# Apache Modules:
	sudo a2enmod ssl
	sudo a2enmod rewrite
	sudo a2enmod suexec
	sudo a2enmod include
	sudo a2enmod proxy
	sudo a2enmod proxy_http
	sudo a2enmod proxy_connect
	sudo a2enmod proxy_ftp
	sudo a2enmod headers
	sudo a2dissite default
	sudo a2dissite default-ssl
	
	echo "Configuring site config files..."
	cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/apache-erp /etc/apache2/sites-available/erp
	mkdir -p /etc/openerp/apache2
	cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/apache-ssl-skeleton /etc/openerp/apache2/ssl-skeleton
	sed -i "s/ServerAdmin webmaster@localhost/ServerAdmin support@clearnet.co.cr\n\n\tInclude \/etc\/apache2\/sites-available\/erp/g" /etc/apache2/sites-available/default
	sed -i "s/ServerAdmin webmaster@localhost/ServerAdmin support@clearnet.co.cr\n\n\tInclude \/etc\/openerp\/apache2\/rewrites/g" /etc/apache2/sites-available/default-ssl

	
	echo "Restarting Apache..."
	/etc/init.d/apache2 restart
fi

#~ TODO: Add shorewall support in ubuntu-server-install, and add rules here

#~ Install phppgadmin
echo "Installing PostgreSQL Web administration interface (phppgadmin)..."
apt-get -qy install phppgadmin
sed -i "s/#\?[[:space:]]*\(deny from all.*\)/# deny from all/g" /etc/phppgadmin/apache.conf
sed -i "s/[[:space:]]*allow from \(.*\)/# allow from \1/g" /etc/phppgadmin/apache.conf
sed -i "s/#\?[[:space:]]*\(allow from all.*\)/allow from all/g" /etc/phppgadmin/apache.conf
sed -i "s/#\?[[:space:]]*\(allow from all.*\)/allow from all/g" /etc/phppgadmin/apache.conf
/etc/init.d/apache2 restart

exit 0
