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
	if [[ $server_type =~ ^[Ww]$ ]]; then
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
	apt-get -qqy install python python-psycopg2 python-reportlab python-egenix-mxdatetime python-tz python-pychart python-pydot python-lxml python-vobject python-imaging python-yaml >> $INSTALL_LOG_FILE
	# Excel spreadsheets generation
	apt-get -qqy install python-xlwt >> $INSTALL_LOG_FILE
	# For nan-tic modules
	apt-get -qqy install postgresql-plpython-8.4 python-qt4 python-dbus python-qt4-dbus pyro >> $INSTALL_LOG_FILE

	# Install the required python libraries for openerp-web.
	echo "Installing the required python libraries for openerp-web..."
	apt-get -qqy install python python-cherrypy3 python-mako python-pybabel python-formencode python-simplejson python-pyparsing >> $INSTALL_LOG_FILE

	# Install the required python libraries for process name change.
	echo "Installing the required python libraries for process name change..."
	apt-get -qqy install python-dev build-essential python-setuptools >> $INSTALL_LOG_FILE
	easy_install -U setproctitle >> $INSTALL_LOG_FILE
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
	/etc/init.d/postgresql-$posgresql_rel restart >> $INSTALL_LOG_FILE
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

function download_openerp_server {
	# Download openerp-server latest stable/trunk release.
	log_echo "Downloading openerp-server latest stable/trunk release..."
	mkdir -p $sources_path >> $INSTALL_LOG_FILE
	cd $sources_path >> $INSTALL_LOG_FILE
	if [ -e openerp-server ]; then
		bzr update openerp-server >> $INSTALL_LOG_FILE
	else
		bzr checkout --lightweight lp:openobject-server/$branch openerp-server >> $INSTALL_LOG_FILE
	fi
	log_echo ""
}

function download_openerp_addons {
	# Download openerp addons latest stable/trunk branch.
	log_echo "Downloading openerp addons latest stable/trunk branch..."
	mkdir -p $sources_path >> $INSTALL_LOG_FILE
	cd $sources_path >> $INSTALL_LOG_FILE
	if [ -e addons ]; then
		bzr update addons >> $INSTALL_LOG_FILE
	else
		bzr checkout --lightweight lp:openobject-addons/$branch addons >> $INSTALL_LOG_FILE
	fi
	log_echo ""
}

function download_ccorp_addons {
	# Download openerp ccorp-addons latest stable/trunk branch.
	log_echo "Downloading openerp ccorp-addons latest stable/trunk branch..."
	mkdir -p $sources_path >> $INSTALL_LOG_FILE
	cd $sources_path >> $INSTALL_LOG_FILE
	if [[ $branch != "trunk" ]]; then
		if [ -e ccorp-addons ]; then
			bzr update ccorp-addons >> $INSTALL_LOG_FILE
		else
			bzr checkout --lightweight lp:openerp-ccorp-addons ccorp-addons >> $INSTALL_LOG_FILE
		fi
	fi
	log_echo ""
}

function download_costa_rica_addons {
	# Download openerp-costa-rica latest stable/trunk branch.
	log_echo "Downloading openerp-costa-rica latest stable/trunk branch..."
	mkdir -p $sources_path >> $INSTALL_LOG_FILE
	cd $sources_path >> $INSTALL_LOG_FILE
	if [[ $branch != "trunk" ]]; then
		if [ -e costa-rica ]; then
			bzr update costa-rica >> $INSTALL_LOG_FILE
		else
			bzr checkout --lightweight lp:openerp-costa-rica costa-rica >> $INSTALL_LOG_FILE
		fi
	fi
	log_echo ""
}

function download_extra_addons {
	# Download extra addons
	log_echo "Downloading extra addons..."
	mkdir -p $sources_path >> $INSTALL_LOG_FILE
	cd $sources_path >> $INSTALL_LOG_FILE
	if [ -e extra-addons ]; then
		bzr update extra-addons >> $INSTALL_LOG_FILE
	else
		bzr checkout --lightweight lp:openobject-addons/extra-$branch extra-addons >> $INSTALL_LOG_FILE
	fi
	log_echo "Removing use_control from extra addons..."
	rm -r extra-addons/use_control >> $INSTALL_LOG_FILE
	log_echo ""
}

function download_magentoerpconnect {
	# Download magentoerpconnect
	log_echo "Downloading magentoerpconnect..."
	mkdir -p $sources_path >> $INSTALL_LOG_FILE
	cd $sources_path >> $INSTALL_LOG_FILE
	if [ -e magentoerpconnect ]; then
		bzr update magentoerpconnect >> $INSTALL_LOG_FILE
	else
		bzr checkout --lightweight lp:magentoerpconnect magentoerpconnect >> $INSTALL_LOG_FILE
	fi
	log_echo ""
}

function download_nan_tic_addons {
	# Download nan-tic modules
	log_echo "Downloading nan-tic modules..."
	mkdir -p $sources_path >> $INSTALL_LOG_FILE
	cd $sources_path >> $INSTALL_LOG_FILE
	if [ -e openobject-client-kde ]; then
		bzr update openobject-client-kde >> $INSTALL_LOG_FILE
	else
		bzr checkout --lightweight lp:~openobject-client-kde/openobject-client-kde/$branch openobject-client-kde >> $INSTALL_LOG_FILE
	fi
	log_echo ""
}

function download_openerp {
	if [[ $branch == "5.0" ]]; then
		download_openerp_server
		if [[ $install_openerp_addons =~ ^[Yy]$ ]]; then download_openerp_addons; fi
		if [[ $install_ccorp_addons =~ ^[Yy]$ ]]; then download_ccorp_addons; fi
		if [[ $install_costa_rica_addons =~ ^[Yy]$ ]]; then download_costa_rica_addons; fi
		if [[ $install_extra_addons =~ ^[Yy]$ ]]; then download_extra_addons; fi
		if [[ $install_magentoerpconnect =~ ^[Yy]$ ]]; then download_magentoerpconnect; fi
		if [[ $install_nantic =~ ^[Yy]$ ]]; then download_nan_tic_addons; fi
	elif [[ $branch == "trunk" ]]; then
		download_openerp_server
		if [[ $install_openerp_addons =~ ^[Yy]$ ]]; then download_openerp_addons; fi
		#if [[ $install_ccorp_addons =~ ^[Yy]$ ]]; then download_ccorp_addons; fi
		#if [[ $install_costa_rica_addons =~ ^[Yy]$ ]]; then download_costa_rica_addons; fi
		#if [[ $install_extra_addons =~ ^[Yy]$ ]]; then download_extra_addons; fi
		#if [[ $install_magentoerpconnect =~ ^[Yy]$ ]]; then download_magentoerpconnect; fi
		#if [[ $install_nantic =~ ^[Yy]$ ]]; then download_nan_tic_addons; fi
	fi
}

function install_openerp_server {
	# Install OpenERP server
	log_echo "Installing OpenERP Server..."
	cd $sources_path/openerp-server >> $INSTALL_LOG_FILE
	#~ Make skeleton installation
	log_echo "Make skeleton installation"
	mkdir -p $install_path >> $INSTALL_LOG_FILE
	cp -a bin/* $install_path/ >> $INSTALL_LOG_FILE
	# Patch openerp-server.py to change process names
	log_echo "Patch openerp-server.py to change process names"
	patch -p1 -i $LIBBASH_CCORP_DIR/install-scripts/openerp-install/openerp-server.py.patch $install_path/openerp-server.py >> $INSTALL_LOG_FILE
	#~ Copy documentation
	log_echo "Copy documentation"
	mkdir -p $base_path/share/doc/openerp-server >> $INSTALL_LOG_FILE
	cp -a doc/* $base_path/share/doc/openerp-server/ >> $INSTALL_LOG_FILE
	#~ Install man pages
	log_echo "Install man pages"
	mkdir -p $base_path/share/man/man1 >> $INSTALL_LOG_FILE
	mkdir -p $base_path/share/man/man5 >> $INSTALL_LOG_FILE
	cp -a man/*.1 $base_path/share/man/man1/ >> $INSTALL_LOG_FILE
	cp -a man/*.5 $base_path/share/man/man5/ >> $INSTALL_LOG_FILE

	#~ Copy bin script skeleton to /etc
	log_echo "Copy bin script skeleton to /etc"
	mkdir -p /etc/openerp/server/ >> $INSTALL_LOG_FILE
	cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/server-bin-skeleton /etc/openerp/server/bin-skeleton >> $INSTALL_LOG_FILE
	# OpenERP Server init and config skeletons
	cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/server-init-skeleton /etc/openerp/server/init-skeleton >> $INSTALL_LOG_FILE
	sed -i "s#\\[PATH\\]#$base_path#g" /etc/openerp/server/init-skeleton >> $INSTALL_LOG_FILE
	cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/server.conf-skeleton /etc/openerp/server/ >> $INSTALL_LOG_FILE
	if [[ $server_type =~ ^[Pp]$ ]]; then
		sed -i "s#\\[LOGLEVEL\\]#info#g" /etc/openerp/server/server.conf-skeleton >> $INSTALL_LOG_FILE
	else
		sed -i "s#\\[LOGLEVEL\\]#debug#g" /etc/openerp/server/server.conf-skeleton >> $INSTALL_LOG_FILE
	fi

	# Make filestore dir
	mkdir -p $install_path/filestore >> $INSTALL_LOG_FILE
	#~ Make pid dir
	mkdir -p /var/run/openerp >> $INSTALL_LOG_FILE
}

function install_openerp_addons {
	# Install OpenERP addons
	log_echo "Installing OpenERP addons..."
	mkdir -p $addons_path >> $INSTALL_LOG_FILE
	cd $sources_path >> $INSTALL_LOG_FILE
	cp -a addons/* $addons_path >> $INSTALL_LOG_FILE
}

function install_ccorp_addons {
	# Install OpenERP ccorp-addons
	log_echo "Installing OpenERP ccorp-addons..."
	cp -a ccorp-addons/* $addons_path >> $INSTALL_LOG_FILE
}

function install_costa_rica_addons {
	# Install OpenERP costa-rica
	log_echo "Installing OpenERP costa-rica..."
	cp -a costa-rica/* $addons_path >> $INSTALL_LOG_FILE
}

function install_extra_addons {
	# Install OpenERP extra addons
	log_echo "Installing OpenERP extra addons..."
	cp -a extra-addons/* $addons_path >> $INSTALL_LOG_FILE
}

function install_magentoerpconnect {
	# Install OpenERP magentoerpconnect
	log_echo "Installing OpenERP magentoerpconnect..."
	cp -a magentoerpconnect $addons_path >> $INSTALL_LOG_FILE
}

function install_nan_tic_addons {
	# Install nan-tic modules
	log_echo "Installing nan-tic modules..."
	rm openobject-client-kde/server-modules/*.sh >> $INSTALL_LOG_FILE
	cp -a openobject-client-kde/server-modules/* $addons_path >> $INSTALL_LOG_FILE
}

function install_change_perms {
	# Change permissions
	chown -R openerp:openerp $install_path_web/openerp* >> $INSTALL_LOG_FILE
	chown -R openerp:openerp /var/log/openerp >> $INSTALL_LOG_FILE
	chown -R openerp:openerp /var/run/openerp >> $INSTALL_LOG_FILE
	chown -R openerp:openerp /etc/openerp >> $INSTALL_LOG_FILE
	chmod -R g+w $install_path >> $INSTALL_LOG_FILE
	chmod -R g+w /var/log/openerp >> $INSTALL_LOG_FILE
	chmod -R g+w /var/run/openerp >> $INSTALL_LOG_FILE
	chmod +x $addons_path >> $INSTALL_LOG_FILE
}

function install_openerp {
	if [[ $branch == "5.0" ]]; then
		install_openerp_server
		if [[ $install_openerp_addons =~ ^[Yy]$ ]]; then install_openerp_addons; fi
		if [[ $install_ccorp_addons =~ ^[Yy]$ ]]; then install_ccorp_addons; fi
		if [[ $install_costa_rica_addons =~ ^[Yy]$ ]]; then install_costa_rica_addons; fi
		if [[ $install_extra_addons =~ ^[Yy]$ ]]; then install_extra_addons; fi
		if [[ $install_magentoerpconnect =~ ^[Yy]$ ]]; then install_magentoerpconnect; fi
		if [[ $install_nantic =~ ^[Yy]$ ]]; then install_nan_tic_addons; fi
	elif [[ $branch == "trunk" ]]; then
		install_openerp_server
		if [[ $install_openerp_addons =~ ^[Yy]$ ]]; then install_openerp_addons; fi
		#if [[ $install_ccorp_addons =~ ^[Yy]$ ]]; then install_ccorp_addons; fi
		#if [[ $install_costa_rica_addons =~ ^[Yy]$ ]]; then install_costa_rica_addons; fi
		#if [[ $install_extra_addons =~ ^[Yy]$ ]]; then install_extra_addons; fi
		#if [[ $install_magentoerpconnect =~ ^[Yy]$ ]]; then install_magentoerpconnect; fi
		#if [[ $install_nantic =~ ^[Yy]$ ]]; then install_nan_tic_addons; fi
	fi
	install_change_perms
}

function download_openerp_web {
	# Download openerp-web latest stable/trunk branch.
	log_echo "Downloading openerp-web latest stable/trunk branch..."
	mkdir -p $sources_path >> $INSTALL_LOG_FILE
	cd $sources_path >> $INSTALL_LOG_FILE
	if [ -e openerp-web ]; then
		bzr update openerp-web >> $INSTALL_LOG_FILE
	else
		bzr checkout --lightweight http://server01.rs.clearcorp.co.cr/bzr/openerp-web-ccorp/$branch openerp-web >> $INSTALL_LOG_FILE
	fi
	log_echo ""
}

function install_openerp_web_client {
	cd $sources_path >> $INSTALL_LOG_FILE

	# Install OpenERP Web client
	log_echo "Installing OpenERP Web client..."
	cp -a openerp-web $install_path_web/openerp-web >> $INSTALL_LOG_FILE

	#~ Copy bin script to /usr/local/bin
	log_echo "Copy bin script /usr/local/bin"
	mkdir -p /usr/local/bin/ >> $INSTALL_LOG_FILE
	cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/web-client/web-client-bin-skeleton /usr/local/bin/openerp-web >> $INSTALL_LOG_FILE

	# OpenERP Web Client init and config skeletons
	mkdir -p /etc/openerp/web-client >> $INSTALL_LOG_FILE
	cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/web-client-init-skeleton /etc/openerp/web-client/init-skeleton >> $INSTALL_LOG_FILE
	sed -i "s#\\[PATH\\]#$base_path#g" /etc/openerp/web-client/init-skeleton >> $INSTALL_LOG_FILE
	cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/web-client.conf-skeleton /etc/openerp/web-client/ >> $INSTALL_LOG_FILE

	#~ Sets server type
	if [[ "$server_type" =~ ^[DdWw]$ ]]; then
		sed -i "s/\[TYPE\]/development/g" /etc/openerp/web-client/web-client.conf-skeleton >> $INSTALL_LOG_FILE
	else
		sed -i "s/\[TYPE\]/production/g" /etc/openerp/web-client/web-client.conf-skeleton >> $INSTALL_LOG_FILE
	fi
}

function install_apache {
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
	fi

	log_echo "Configuring site config files..."
	cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/apache-erp /etc/apache2/sites-available/erp >> $INSTALL_LOG_FILE
	mkdir -p /etc/openerp/apache2/rewrites >> $INSTALL_LOG_FILE
	cp $LIBBASH_CCORP_DIR/install-scripts/openerp-install/apache-ssl-skeleton /etc/openerp/apache2/ssl-skeleton >> $INSTALL_LOG_FILE
	sed -i "s/ServerAdmin webmaster@localhost/ServerAdmin support@clearnet.co.cr\n\n\tInclude \/etc\/apache2\/sites-available\/erp/g" /etc/apache2/sites-available/default >> $INSTALL_LOG_FILE
	sed -i "s/ServerAdmin webmaster@localhost/ServerAdmin support@clearnet.co.cr\n\n\tInclude \/etc\/openerp\/apache2\/rewrites/g" /etc/apache2/sites-available/default-ssl >> $INSTALL_LOG_FILE


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

function make_menus {
	#~ Make developer menus
	if [[ $type == "station" ]]; then
		sudo -u $openerp_user $LIBBASH_CCORP_DIR/install-scripts/openerp-install/mkmenus-ccorp-main.sh
	fi
	exit 0
}

function add_log_rotation {
	cat << EOF > /etc/logrotate.d/openerp
/var/log/openerp/*.log /var/log/openerp/*/*.log {
	daily
	rotate 30
	compress
	nodelaycompress
	nocopytruncate
	ifempty
	nomissingok
	create 664 openerp openerp
	noolddir
}
EOF
}
