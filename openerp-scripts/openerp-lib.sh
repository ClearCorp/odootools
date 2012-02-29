#       openerp-lib.sh
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

function log {
	echo "$(date): $1" >> $INSTALL_LOG_FILE
}

function log_echo {
	echo $1
	log "$1"
}

function openerp_get_dist {
	
	# Sets vars corresponding to the distro
	if [[ $dist == "lucid" ]]; then
		# Ubuntu 10.04, python 2.6
		posgresql_rel=8.4
		python_rel=python2.6
		ubuntu_rel=10.04
	elif [[ $dist == "maverick" ]]; then
		# Ubuntu 10.10, python 2.6
		posgresql_rel=8.4
		posgresql_init="-8.4"
		python_rel=python2.6
		ubuntu_rel=10.10
	elif [[ $dist == "natty" ]]; then
		# Ubuntu 11.04, python 2.6
		posgresql_rel=8.4
		python_rel=python2.6
		ubuntu_rel=11.04
	elif [[ $dist == "oneiric" ]]; then
		# Ubuntu 11.10, python 2.7, postgres 9.1
		posgresql_rel=9.1
		python_rel=python2.7
		ubuntu_rel=11.10
	else
		# Only Lucid supported for now
		log_echo "ERROR: This program must be executed on Ubuntu 10.04 - 11.10 (Desktop or Server)"
		exit 1
	fi
}

function check_system_values {
	log_echo "Hostname: `hostname`"
	log_echo "FQDN: `hostname --fqdn`"
	log_echo "Time and date: `date`"
	log_echo "Installed locales:"
	log_echo "`for i in $(ls /var/lib/locales/supported.d/*); do cat $i; done`"
	log_echo "Default locale: `echo $LC_ALL`"
	log_echo ""
	log_echo "Please check this values. If there is something to correct, do it BEFORE installing or updating OpenERP."
	log_echo "The ccorp-ubuntu-server-install script can help you setting this."
	while [[ ! $tmp =~ ^[CcQq]$ ]]; do
		read -p "Do you want to Continue or Quit (c/q)? " -n 1 tmp
		log_echo ""
	done
	if [[ $tmp =~ ^[Cc]$ ]]; then
		return 0
	else
		return 1
	fi
	return 1
}

function add_openerp_user {
	log_echo "Adding openerp user..."
	adduser --system --home /var/run/openerp --no-create-home --group openerp >> $INSTALL_LOG_FILE
	#Add group in case the user existed without a group (previous versions)
	addgroup openerp >> $INSTALL_LOG_FILE
	if [[ $server_type =~ ^station$ ]]; then
		adduser $openerp_user openerp
	fi
	log_echo ""
}

function update_system {
	log_echo "Updating the system..."
	apt-get -qy update >> $INSTALL_LOG_FILE
	apt-get -qy upgrade >> $INSTALL_LOG_FILE
	log_echo ""
}

function install_python_lib {
	# Install the required packages and python libraries for openerp.
	echo "Installing the required packages and python libraries for openerp..."
	
	# Package array
	declare -a packages
	
	# Packages need by the installer
	packages+=(python-setuptools)

	# Packages for all server versions
	# Dependencies
	packages+=(python-lxml)
	packages+=(python-psycopg2)
	packages+=(python-pychart)
	packages+=(python-pydot)
	packages+=(python-reportlab)
	packages+=(python-tz)
	packages+=(python-vobject)
	# Recomended
	packages+=(graphviz)
	packages+=(ghostscript)
	packages+=(python-imaging)
	packages+=(python-libxslt1)	#Excel spreadsheets
	packages+=(python-matplotlib)
	packages+=(python-openssl)	#Extra for ssl ports
	packages+=(python-xlwt)		#Excel spreadsheets

	# Packages for 5.0 server
	if [[ $branch =~ "5.0" ]]; then
		#Dependencies
		packages+=(python-egenix-mxdatetime)
		
		#Recommended
		packages+=(python-pyparsing)
	fi

	# Packages for 6.0 and 6.1 servers
	if [[ $branch =~ "6.0" ]] || [[ $branch =~ "6.1" ]] || [[ $branch =~ "trunk" ]]; then
		# Dependencies
		packages+=(python-dateutil)
		packages+=(python-feedparser)
		packages+=(python-mako)
		packages+=(python-pyparsing)
		packages+=(python-yaml)

		# Recomended
		packages+=(python-webdav)		#For document-webdav
	fi

	# Packages for 6.1 server
	if [[ $branch =~ "6.1" ]] || [[ $branch =~ "trunk" ]]; then
		# Dependencies
		packages+=(python-werkzeug)
		packages+=(python-zsi)
	
		# Recomended
		packages+=(python-gdata)		#Google data parser
		packages+=(python-ldap)
		packages+=(python-openid)
		packages+=(python-vatnumber)
	fi

	# Packages for all web client versions
	# Dependencies
	packages+=(python-formencode)
	packages+=(python-pybabel)
	packages+=(python-simplejson)
	packages+=(python-pyparsing)

	# Packages for 5.0 web client
	if [[ $branch =~ "5.0" ]]; then
		#Recommended
		packages+=(libjs-mochikit)
		packages+=(libjs-mootools)
		packages+=(python-beaker)
		packages+=(tinymce)
	fi

	# Packages for 5.0 and 6.0 servers
	if [[ $branch =~ "5.0" ]] || [[ $branch =~ "6.0" ]]; then
		# Dependencies
		packages+=(python-cherrypy3)
	fi

	# Packages for 6.1 server
	if [[ $branch =~ "6.1" ]] || [[ $branch =~ "trunk" ]]; then
		# Dependencies
		packages+=(python-werkzeug)
	
		# Recomended
		packages+=(python-mock)			# For testing
		packages+=(python-unittest2)	# For testing
	fi
	
	# Install packages
	apt-get -qy install ${packages[*]} >> $INSTALL_LOG_FILE
}

function install_bzr {
	# Install bazaar.
	log_echo "Installing bazaar..."
	apt-get -qy install bzr >> $INSTALL_LOG_FILE
	log_echo ""
}

function install_postgresql {
	# Install postgresql
	log_echo "Installing postgresql..."
	apt-get -qy install postgresql >> $INSTALL_LOG_FILE
	log_echo ""
}

function update_pg_hba {
	# Update pg_hba.conf
	sed -i 's/\(local[[:space:]]*all[[:space:]]*all[[:space:]]*\)\(ident[[:space:]]*sameuser\)/\1md5/g' /etc/postgresql/$posgresql_rel/main/pg_hba.conf >> $INSTALL_LOG_FILE
	/etc/init.d/postgresql$posgresql_init restart >> $INSTALL_LOG_FILE
	log_echo ""
}

function add_postgres_user {
	/usr/bin/sudo -u postgres createuser openerp --superuser --createdb --no-createrole >> $INSTALL_LOG_FILE
	/usr/bin/sudo -u postgres psql template1 -U postgres -c "alter user openerp with password '$openerp_admin_passwd'" >> $INSTALL_LOG_FILE
	log_echo ""
}

function change_postgres_passwd {
	log_echo "Changing postgres user password on request..."
	log_echo "postgres:$postgres_admin_passwd" | chpasswd
	sudo -u postgres psql template1 -U postgres -c "alter user postgres with password '$postgres_admin_passwd'" >> $INSTALL_LOG_FILE
	log_echo ""
}

function download_openerp_branch {
	# $1: sources branch
	# $2: launchpad project
	# $3: launchpad branch
	# Download branch latest release.
	log_echo "Downloading $1 latest $branch release..."
	mkdir -p /srv/openerp/$branch/src >> $INSTALL_LOG_FILE
	cd /srv/openerp/$branch/src >> $INSTALL_LOG_FILE
	if [ -e $1 ]; then
		cd $1 >> $INSTALL_LOG_FILE
		bzr pull >> $INSTALL_LOG_FILE
	else
		mkdir -p /usr/local/src/openerp/$branch >> $INSTALL_LOG_FILE
		cd /usr/local/src/openerp/$branch >> $INSTALL_LOG_FILE
		if [[ ! -f $1.tgz ]]; then
			wget http://code.clearcorp.co.cr/bzr/openerp/openerp-src/bin/$branch/$1.tgz >> $INSTALL_LOG_FILE
		fi
		cd .. >> $INSTALL_LOG_FILE
		tar xzf $branch/$1.tgz >> $INSTALL_LOG_FILE
		bzr branch $branch/$1 /srv/openerp/$branch/src/$1 >> $INSTALL_LOG_FILE
		rm -r $branch/$1 >> $INSTALL_LOG_FILE
		echo "parent_location = lp:~clearcorp/$2/$3" > /srv/openerp/$branch/src/$1/.bzr/branch/branch.conf
		cd /srv/openerp/$branch/src/$1 >> $INSTALL_LOG_FILE
		bzr pull
	fi
	log_echo ""
}

function download_other_branch {
	# $1: sources branch
	# $2: launchpad project
	# $3: launchpad branch
	# Download branch latest release.
	log_echo "Downloading $1 latest $branch release..."
	mkdir -p /srv/openerp/$branch/src >> $INSTALL_LOG_FILE
	cd /srv/openerp/$branch/src >> $INSTALL_LOG_FILE
	if [ -e $1 ]; then
		cd $1 >> $INSTALL_LOG_FILE
		bzr pull >> $INSTALL_LOG_FILE
	else
		bzr branch lp:$2/$3 $1 >> $INSTALL_LOG_FILE
	fi
	log_echo ""
}

function download_openerp {
	bzr init-repo /srv/openerp
	if [[ $branch == "5.0" ]] || [[ $branch == "6.0" ]] || [[ $branch == "6.1" ]] || [[ $branch == "trunk" ]]; then
		download_openerp_branch openobject-server openobject-server $branch-ccorp
		if [[ $install_openerp_addons =~ ^[Yy]$ ]]; then
			download_openerp_branch openobject-addons openobject-addons $branch-ccorp
		fi
		if [[ $install_extra_addons =~ ^[Yy]$ ]]; then
			download_openerp_branch openobject-addons-extra openobject-addons extra-$branch-ccorp
		fi
		if [[ $install_ccorp_addons =~ ^[Yy]$ ]]; then
			download_other_branch openerp-ccorp-addons openerp-ccorp-addons $branch
		fi
		if [[ $install_costa_rica_addons =~ ^[Yy]$ ]]; then
			download_other_branch openerp-costa-rica openerp-costa-rica $branch
		fi
	fi
}

function install_openerp_server {
	# Install OpenERP server
	log_echo "Installing OpenERP Server..."

	#~ Copy bin script skeleton to /etc
	log_echo "Copy bin script skeleton to /etc"
	mkdir -p /etc/openerp/$branch/server/ >> $INSTALL_LOG_FILE
	cp $OPENERP_CCORP_DIR/openerp-scripts/server/server-bin-skeleton /etc/openerp/$branch/server/bin-skeleton >> $INSTALL_LOG_FILE
	sed -i "s#\\[BRANCH\\]#$branch#g" /etc/openerp/$branch/server/bin-skeleton >> $INSTALL_LOG_FILE
	# OpenERP Server init
	cp $OPENERP_CCORP_DIR/openerp-scripts/server/server-init-$branch-skeleton /etc/openerp/$branch/server/init-$branch-skeleton >> $INSTALL_LOG_FILE
	sed -i "s#\\[PATH\\]#/usr/local#g" /etc/openerp/$branch/server/init-$branch-skeleton >> $INSTALL_LOG_FILE
	# OpenERP Server config skeletons
	cp $OPENERP_CCORP_DIR/openerp-scripts/server/server.conf-$branch-skeleton /etc/openerp/$branch/server/ >> $INSTALL_LOG_FILE
	sed -i "s#\\[BRANCH\\]#$branch#g" /etc/openerp/$branch/server/server.conf-$branch-skeleton >> $INSTALL_LOG_FILE
	if [[ $server_type =~ ^production$ ]]; then
		sed -i "s#\\[LOGLEVEL\\]#info#g" /etc/openerp/$branch/server/server.conf-$branch-skeleton >> $INSTALL_LOG_FILE
		sed -i "s#\\[DEBUGMODE\\]#False#g" /etc/openerp/$branch/server/server.conf-$branch-skeleton >> $INSTALL_LOG_FILE
	else
		sed -i "s#\\[LOGLEVEL\\]#debug#g" /etc/openerp/$branch/server/server.conf-$branch-skeleton >> $INSTALL_LOG_FILE
		sed -i "s#\\[DEBUGMODE\\]#True#g" /etc/openerp/$branch/server/server.conf-$branch-skeleton >> $INSTALL_LOG_FILE
	fi
	
	#~ Make pid dir
	mkdir -p /var/run/openerp >> $INSTALL_LOG_FILE

	# Make SSL certificates
	mkdir -p /etc/openerp/ssl/private
	mkdir -p /etc/openerp/ssl/signedcerts
	mkdir -p /etc/openerp/ssl/servers
	cd /etc/openerp/ssl

	echo '01' > serial  && touch index.txt
	cp $OPENERP_CCORP_DIR/openerp-scripts/server/ca.cnf /etc/openerp/ssl/ca.cnf >> $INSTALL_LOG_FILE
	cp $OPENERP_CCORP_DIR/openerp-scripts/server/server.cnf /etc/openerp/ssl/server.cnf-skeleton >> $INSTALL_LOG_FILE

	openssl req -x509 -newkey rsa:2048 -out cacert.pem -outform PEM -days 1825 -config ca.cnf -passout pass:$openerp_admin_passwd
	openssl x509 -in cacert.pem -out cacert.crt

}

function install_change_perms {
	# Change permissions
	chown -R $openerp_user:openerp /srv/openerp >> $INSTALL_LOG_FILE
	chown -R $openerp_user:openerp /var/log/openerp >> $INSTALL_LOG_FILE
	chown -R $openerp_user:openerp /var/run/openerp >> $INSTALL_LOG_FILE
	chown -R $openerp_user:openerp /etc/openerp >> $INSTALL_LOG_FILE
	chmod -R g+w /srv/openerp >> $INSTALL_LOG_FILE
	chmod -R g+w /var/log/openerp >> $INSTALL_LOG_FILE
	chmod -R g+w /var/run/openerp >> $INSTALL_LOG_FILE
	for x in $(ls -d /srv/openerp/$branch/instances/*/addons); do
		chmod +x $x >> $INSTALL_LOG_FILE;
	done
}

function install_openerp {
	install_openerp_server
	install_change_perms
}

function download_openerp_web {
	if [[ $branch == "5.0" ]] || [[ $branch == "6.0" ]]; then
		download_openerp_branch openobject-client-web openobject-client-web $branch-ccorp
	elif [[ $branch == "6.1" ]] || [[ $branch == "trunk" ]]; then
		download_openerp_branch openerp-web openerp-web $branch-ccorp
	fi
}

function install_openerp_web_client {
	# Install OpenERP Web client
	log_echo "Installing OpenERP Web client..."

	#~ Copy bin script
	log_echo "Copy bin script"
	mkdir -p /etc/openerp/$branch/web-client >> $INSTALL_LOG_FILE
	cp $OPENERP_CCORP_DIR/openerp-scripts/web-client/web-client-bin-skeleton /etc/openerp/$branch/web-client/bin-skeleton >> $INSTALL_LOG_FILE
	sed -i "s#\\[BRANCH\\]#$branch#g" /etc/openerp/$branch/web-client/bin-skeleton >> $INSTALL_LOG_FILE

	# OpenERP Web Client init and config skeletons
	log_echo "Copy init script"
	cp $OPENERP_CCORP_DIR/openerp-scripts/web-client/web-client-init-skeleton /etc/openerp/$branch/web-client/init-skeleton >> $INSTALL_LOG_FILE
	sed -i "s#\\[BRANCH\\]#$branch#g" /etc/openerp/$branch/web-client/init-skeleton >> $INSTALL_LOG_FILE
	log_echo "Copy config"
	cp $OPENERP_CCORP_DIR/openerp-scripts/web-client/web-client.conf-$branch-skeleton /etc/openerp/$branch/web-client/ >> $INSTALL_LOG_FILE

	#~ Sets server type
	if [[ "$server_type" =~ ^development|station$ ]]; then
		sed -i "s/dbbutton\.visible = False/dbbutton.visible = True/g" /etc/openerp/$branch/web-client/web-client.conf-$branch-skeleton >> $INSTALL_LOG_FILE
		sed -i "s/\[TYPE\]/development/g" /etc/openerp/$branch/web-client/web-client.conf-$branch-skeleton >> $INSTALL_LOG_FILE
	else
		sed -i "s/\[TYPE\]/production/g" /etc/openerp/$branch/web-client/web-client.conf-$branch-skeleton >> $INSTALL_LOG_FILE
	fi
	
	#Change perms
	install_change_perms
}

function install_apache {
	## Apache installation

	if [[ "$install_apache" =~ ^[Yy]$ ]]; then
		log_echo "Installing Apache..."
		apt-get -qqy install apache2 >> $INSTALL_LOG_FILE

		log_echo "Making SSL certificate for Apache...";
		make-ssl-cert generate-default-snakeoil >> $INSTALL_LOG_FILE
		# Snakeoil certificate files:
		# /usr/share/ssl-cert/ssleay.cnf
		# /etc/ssl/certs/ssl-cert-snakeoil.pem
		# /etc/ssl/private/ssl-cert-snakeoil.key

		log_echo "Enabling Apache Modules..."
		# Apache Modules:
		a2enmod ssl rewrite suexec include proxy proxy_http proxy_connect proxy_ftp headers >> $INSTALL_LOG_FILE
		a2ensite default default-ssl >> $INSTALL_LOG_FILE
	fi

	log_echo "Configuring site config files..."
	cp $OPENERP_CCORP_DIR/openerp-scripts/apache-erp /etc/apache2/sites-available/erp >> $INSTALL_LOG_FILE
	mkdir -p /etc/openerp/apache2/rewrites >> $INSTALL_LOG_FILE
	cp $OPENERP_CCORP_DIR/openerp-scripts/apache-ssl-$branch-skeleton /etc/openerp/apache2/ssl-$branch-skeleton >> $INSTALL_LOG_FILE
	sed -i "s/ServerAdmin .*$/ServerAdmin support@clearcorp.co.cr\n\n\tInclude \/etc\/apache2\/sites-available\/erp/g" /etc/apache2/sites-available/default >> $INSTALL_LOG_FILE
	sed -i "s/ServerAdmin .*$/ServerAdmin support@clearcorp.co.cr\n\n\tInclude \/etc\/openerp\/apache2\/rewrites/g" /etc/apache2/sites-available/default-ssl >> $INSTALL_LOG_FILE


	log_echo "Restarting Apache..."
	/etc/init.d/apache2 restart >> $INSTALL_LOG_FILE
}

function install_phppgadmin {
	#~ Install phppgadmin
	log_echo "Installing PostgreSQL Web administration interface (phppgadmin)..."
	apt-get -qy install phppgadmin >> $INSTALL_LOG_FILE
	sed -i "s/#\?[[:space:]]*\(deny from all.*\)/# deny from all/g" /etc/phppgadmin/apache.conf >> $INSTALL_LOG_FILE
	sed -i "s/[[:space:]]*allow from \(.*\)/# allow from \1/g" /etc/phppgadmin/apache.conf >> $INSTALL_LOG_FILE
	sed -i "s/#\?[[:space:]]*\(allow from all.*\)/allow from all/g" /etc/phppgadmin/apache.conf >> $INSTALL_LOG_FILE
	sed -i "s/#\?[[:space:]]*\(allow from all.*\)/allow from all/g" /etc/phppgadmin/apache.conf >> $INSTALL_LOG_FILE
	/etc/init.d/apache2 restart >> $INSTALL_LOG_FILE
}

function mkserver_addons_mk_links {
	# Create symbolic links for addons
	# $1: project (src branch)
	log_echo "Creating symbolic links for $1..."
	cd /srv/openerp/$branch/src/$1 >> $INSTALL_LOG_FILE
    if [[ $branch == "6.1" ]] || [[ $branch == "trunk" ]]; then
        mkdir /srv/openerp/$branch/instances/$name/addons/$1
        for x in $(ls -d *); do
            if [[ -d /srv/openerp/$branch/instances/$name/addons/$1/$x ]]; then
                log_echo "$1: module $x already present, skipping"
            else
                ln -s /srv/openerp/$branch/src/$1/$x /srv/openerp/$branch/instances/$name/addons/$1/$x >> $INSTALL_LOG_FILE
            fi
        done
    else
        for x in $(ls -d *); do
            if [[ -d /srv/openerp/$branch/instances/$name/addons/$x ]]; then
                log_echo "$1: module $x already present, skipping"
            else
                ln -s /srv/openerp/$branch/src/$1/$x /srv/openerp/$branch/instances/$name/addons/$x >> $INSTALL_LOG_FILE
            fi
        done
    fi
}

function mkserver_addons_rm_links {
	# Remove symbolic links for addons
	log_echo "Removing symbolic links for $name..."
	cd /srv/openerp/$branch/instances/$name/addons >> $INSTALL_LOG_FILE
	for x in $(ls -d *); do
		if [[ -h /srv/openerp/$branch/instances/$name/addons/$x ]]; then
			log_echo "$x is a symbolic linked addon, removing"
			rm $x >> $INSTALL_LOG_FILE
		else
			log_echo "$x is not a symbolic linked addon, skipping"
		fi
	done
}

function mkserver_install_addons {
	if [[ $install_openerp_addons =~ ^[Yy]$ ]]; then mkserver_addons_mk_links openobject-addons; fi
	if [[ $install_ccorp_addons =~ ^[Yy]$ ]]; then mkserver_addons_mk_links openerp-ccorp-addons; fi
	if [[ $install_costa_rica_addons =~ ^[Yy]$ ]]; then mkserver_addons_mk_links openerp-costa-rica; fi
	if [[ $install_extra_addons =~ ^[Yy]$ ]]; then mkserver_addons_mk_links openobject-addons-extra; fi
	if [[ $install_magentoerpconnect =~ ^[Yy]$ ]]; then mkserver_addons_mk_links magentoerpconnect; fi
	if [[ $install_nantic =~ ^[Yy]$ ]]; then mkserver_addons_mk_links nantic; fi
}

function make_menus {
	#~ Make developer menus
	if [[ $server_type == "station" ]]; then
		su $openerp_user -c $OPENERP_CCORP_DIR/openerp-scripts/mkmenus-ccorp-main.sh
	fi
}

function add_log_rotation {
	rm /etc/logrotate.d/openerp*
	cp $OPENERP_CCORP_DIR/openerp-scripts/scripts/openerp.logrotate /etc/logrotate.d/
}
