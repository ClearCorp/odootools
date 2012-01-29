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
	apt-get -qq update >> $INSTALL_LOG_FILE
	apt-get -qqy upgrade >> $INSTALL_LOG_FILE
	log_echo ""
}

function install_python_lib {
	# Install the required python libraries for openerp-server.
	echo "Installing the required python libraries for openerp-server..."
	# From doc.openerp.com
	apt-get -qqy install python python-psycopg2 python-reportlab python-egenix-mxdatetime python-tz python-pychart python-pydot python-lxml python-vobject python-imaging python-yaml python-mako >> $INSTALL_LOG_FILE
	# Excel spreadsheets generation
	apt-get -qqy install python-xlwt >> $INSTALL_LOG_FILE
	# For nan-tic modules
	apt-get -qqy install postgresql-plpython python-qt4 python-dbus python-qt4-dbus pyro >> $INSTALL_LOG_FILE

	# Install the required python libraries for openerp-web.
	echo "Installing the required python libraries for openerp-web..."
	apt-get -qqy install python python-cherrypy3 python-mako python-pybabel python-formencode python-simplejson python-pyparsing >> $INSTALL_LOG_FILE

	# Install the required python libraries for process name change.
	echo "Installing the required python libraries for process name change..."
	apt-get -qqy install python-dev build-essential python-setuptools >> $INSTALL_LOG_FILE
	easy_install -U setproctitle >> $INSTALL_LOG_FILE

	# Install the required python libraries for webdav
	echo "Installing the required python libraries for webdav..."
	easy_install -U pywebdav >> $INSTALL_LOG_FILE
	log_echo ""
}

function install_bzr {
	# Install bazaar.
	log_echo "Installing bazaar..."
	apt-get -qqy install bzr >> $INSTALL_LOG_FILE
	log_echo ""
}

function install_postgresql {
	# Install postgresql
	log_echo "Installing postgresql..."
	apt-get -qqy install postgresql >> $INSTALL_LOG_FILE
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
		mkdir -p /tmp/openerp-ccorp-scripts >> $INSTALL_LOG_FILE
		cd /tmp/openerp-ccorp-scripts >> $INSTALL_LOG_FILE
		wget http://www.wuala.com/carlos.vasquez/openerp-src-bin/$branch/$1.tgz >> $INSTALL_LOG_FILE
		tar xzf $1.tgz >> $INSTALL_LOG_FILE
		bzr branch $branch/$1 /srv/openerp/$branch/src/$1 >> $INSTALL_LOG_FILE
		echo "parent_location = lp:~clearcorp/$2/$3" > /srv/openerp/$branch/src/$1/.bzr/branch/branch.conf
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
	if [[ $branch == "5.0" ]] || [[ $branch == "6.0" ]] || [[ $branch == "trunk" ]]; then
		download_openerp_branch openobject-server openobject-server ccorp-$branch
		if [[ $install_openerp_addons =~ ^[Yy]$ ]]; then
			download_openerp_branch openobject-addons openobject-addons ccorp-$branch
		fi
		if [[ $install_extra_addons =~ ^[Yy]$ ]]; then
			download_openerp_branch openobject-addons-extra openobject-addons ccorp-extra-$branch
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
		download_openerp_branch openobject-client-web openobject-client-web ccorp-$branch
	elif [[ $branch == "trunk" ]]; then
		download_openerp_branch openerp-web openerp-web ccorp-$branch
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

function mkserver_openerp_addons {
	# Install OpenERP addons
	log_echo "Installing OpenERP addons..."
	cd /srv/openerp/$branch/src/openobject-addons >> $INSTALL_LOG_FILE
	for x in $(ls -d *); do
		if [[ -d /srv/openerp/$branch/instances/$name/addons/$x ]]; then
			log_echo "openobject-addons: module $x already present, removing"
			rm -r /srv/openerp/$branch/instances/$name/addons/$x >> $INSTALL_LOG_FILE
		fi
		ln -s /srv/openerp/$branch/src/openobject-addons/$x /srv/openerp/$branch/instances/$name/addons/$x >> $INSTALL_LOG_FILE
	done
}

function mkserver_ccorp_addons {
	# Install ccorp addons
	log_echo "Installing ccorp addons..."
	cd /srv/openerp/$branch/src/ccorp-addons >> $INSTALL_LOG_FILE
	for x in $(ls -d *); do
		if [[ -d /srv/openerp/$branch/instances/$name/addons/$x ]]; then
			log_echo "ccorp-addons: module $x already present, removing"
			rm -r /srv/openerp/$branch/instances/$name/addons/$x >> $INSTALL_LOG_FILE
		fi
		ln -s /srv/openerp/$branch/src/ccorp-addons/$x /srv/openerp/$branch/instances/$name/addons/$x >> $INSTALL_LOG_FILE
	done
}

function mkserver_costa_rica_addons {
	# Install OpenERP costa-rica
	log_echo "Installing OpenERP costa-rica..."
	cd /srv/openerp/$branch/src/costa-rica-addons >> $INSTALL_LOG_FILE
	for x in $(ls -d *); do
		if [[ -d /srv/openerp/$branch/instances/$name/addons/$x ]]; then
			log_echo "costa-rica-addons: module $x already present, removing"
			rm -r /srv/openerp/$branch/instances/$name/addons/$x >> $INSTALL_LOG_FILE
		fi
		ln -s /srv/openerp/$branch/src/costa-rica-addons/$x /srv/openerp/$branch/instances/$name/addons/$x >> $INSTALL_LOG_FILE
	done
}

function mkserver_extra_addons {
	# Install OpenERP extra addons
	log_echo "Installing OpenERP extra addons..."
	cd /srv/openerp/$branch/src/openobject-addons-extra >> $INSTALL_LOG_FILE
	for x in $(ls -d *); do
		if [[ -d /srv/openerp/$branch/instances/$name/addons/$x ]]; then
			log_echo "openobject-addons-extra: module $x already present, removing"
			rm -r /srv/openerp/$branch/instances/$name/addons/$x >> $INSTALL_LOG_FILE
		fi
		ln -s /srv/openerp/$branch/src/openobject-addons-extra/$x /srv/openerp/$branch/instances/$name/addons/$x >> $INSTALL_LOG_FILE
	done
}

function mkserver_nan_tic_addons {
	# Install nan-tic modules
	log_echo "Installing nan-tic modules..."
	cd /srv/openerp/$branch/src/nan-tic-addons >> $INSTALL_LOG_FILE
	for x in $(ls -d *); do
		if [[ -d /srv/openerp/$branch/instances/$name/addons/$x ]]; then
			log_echo "nan-tic-addons: module $x already present, removing"
			rm -r /srv/openerp/$branch/instances/$name/addons/$x >> $INSTALL_LOG_FILE
		fi
		ln -s /srv/openerp/$branch/src/nan-tic-addons/$x /srv/openerp/$branch/instances/$name/addons/$x >> $INSTALL_LOG_FILE
	done
}

function mkserver_install_addons {
	if [[ $install_nantic =~ ^[Yy]$ ]]; then mkserver_nan_tic_addons; fi
	if [[ $install_magentoerpconnect =~ ^[Yy]$ ]]; then mkserver_magentoerpconnect; fi
	if [[ $install_extra_addons =~ ^[Yy]$ ]]; then mkserver_extra_addons; fi
	if [[ $install_costa_rica_addons =~ ^[Yy]$ ]]; then mkserver_costa_rica_addons; fi
	if [[ $install_ccorp_addons =~ ^[Yy]$ ]]; then mkserver_ccorp_addons; fi
	if [[ $install_openerp_addons =~ ^[Yy]$ ]]; then mkserver_openerp_addons; fi
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
