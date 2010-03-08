#!/bin/bash

#~ Go to libbash-ccorp directory
cd /usr/local/share/libbash-ccorp

# Libraries import
. main-lib/checkRoot.sh
. main-lib/getDist.sh

# Check user is root
checkRoot

# Print title
echo "OpenERP installation script."
echo ""

# Set distribution
dist=""
getDist dist

# Sets vars corresponding to the distro
if [[ $dist == "hardy" ]]; then
	# Ubuntu 8.04, python 2.5
	posgresql_rel=8.3
	python_rel=python2.5
	ubuntu_rel=8.04
	install_path=/usr
	addons_path=$install_path/lib/$python_rel/site-packages/openerp-server/addons/
elif [[ $dist == "karmic" ]]; then
	# Ubuntu 9.10, python 2.6
	posgresql_rel=8.4
	python_rel=python2.6
	ubuntu_rel=9.10
	install_path=/usr/local
	addons_path=$install_path/lib/$python_rel/dist-packages/openerp-server/addons/
else
	# Check that the script is run on Ubuntu Hardy or Ubuntu Karmic
	echo "This program must be executed on Ubuntu 8.04.3 LTS or Ubuntu 9.10 (Desktop or Server)"
	exit 1
fi

# Run the Ubuntu preparation script.
while [[ ! $run_preparation_script =~ ^[YyNn]$ ]]; do
	read -p "Do you want to run the Ubuntu preparation script (recommended if not done) (y/N)? " -n 1 run_preparation_script
	if [[ $run_preparation_script == "" ]]; then
		run_preparation_script="n"
	fi
	echo ""
done
if [[ $run_preparation_script =~ ^[Yy]$ ]]; then
        echo ""
	ubuntu-server-install/ubuntu-server-install.sh
fi


# Initial questions
####################

#Choose the branch to install
while [[ ! $branch =~ ^[SsTt]$ ]]; do
	read -p "Which branch do you want to install (Stable/trunk)? " -n 1 branch
	if [[ $branch == "" ]]; then
		branch="s"
	fi
	echo ""
done
if [[ $branch =~ ^[Ss]$ ]]; then
	branch="5.0"
else
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
		read -p "Enter the OpenERP administrator password: " openerp_admin_passwd2
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

#Set the postgre admin password
while [[ ! $set_postgre_admin_passwd =~ ^[YyNn]$ ]]; do
        read -p "Would you like to change the postgre user password (Y/n)? " -n 1 set_postgre_admin_passwd
        if [[ $set_postgre_admin_passwd == "" ]]; then
                set_postgre_admin_passwd="y"
        fi
        echo ""
done
if [[ $set_postgre_admin_passwd =~ ^[Yy]$ ]]; then
	postgre_admin_passwd=""
	while [[ $postgre_admin_passwd == "" ]]; do
		read -p "Enter the postgre user password: " postgre_admin_passwd
		if [[ $postgre_admin_passwd == "" ]]; then
			echo "The password cannot be empty."
		else
			read -p "Enter the postgre user password again: " postgre_admin_passwd2
			echo ""
			if [[ $openerp_admin_passwd == $openerp_admin_passwd2 ]]; then
				echo "postgre user password set."
			else
				postgre_admin_passwd=""
				echo "Passwords don't match."
			fi
		fi
		echo ""
	done
fi

#Preparing installation
#######################

echo "Preparing installation."

#Add openerp user
echo "Adding openerp user."
adduser --quiet --system openerp
echo ""

# Update the system.
echo "Updating the system."
apt-get update
apt-get -y upgrade
echo ""

# Install the required python libraries for openerp-server.
echo "Installing the required python libraries for openerp-server."
apt-get -y install python python-psycopg2 python-reportlab python-egenix-mxdatetime python-tz python-pychart python-pydot python-lxml python-libxslt1 python-vobject python-imaging python-dev build-essential python-setuptools python-profiler
echo ""

# Install bazaar.
echo "Installing bazaar."
apt-get -y install bzr
bzr whoami "ClearCorp S.A. <info@clearcorp.co.cr>"
echo ""

# Install postgresql
echo "Installing postgresql."
apt-get -y install postgresql
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

# Add openerp postgre user
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

# Change postgre user password
echo "Changing postgre user password on request."
if [[ $set_postgre_admin_passwd =~ ^[Yy]$ ]]; then
	chpasswd postgre:$postgre_admin_passwd
	sudo -u postgres psql template1 -U postgres -c "alter user postgres with password '$postgre_admin_passwd'"
fi


# Downloading OpenERP
#####################

echo "Downloading OpenERP."
echo ""

cd /usr/local/src

# Download openerp-server latest stable/trunk release.
echo "Downloading openerp-server latest stable/trunk release."
bzr checkout --lightweight lp:openobject-server/$branch openerp-server
echo ""

# Download openerp-client-web latest stable release.
echo "Downloading openerp-client-web latest stable release."
bzr checkout --lightweight lp:openobject-client-web/$branch openerp-web
echo ""

# Download openerp addons latest stable/trunk branch.
echo "Downloading openerp addons latest stable/trunk branch."
bzr checkout --lightweight lp:openobject-addons/$branch addons
echo ""

# Download extra addons
if [[ $install_extra_addons =~ ^[Yy]$ ]]; then
	echo "Downloading extra addons"
	bzr checkout --lightweight lp:openobject-addons/extra-$branch extra-addons
	echo ""
fi

# Download magentoerpconnect
if [[ $install_magentoerpconnect =~ ^[Yy]$ ]]; then
	echo "Downloading magentoerpconnect."
	bzr checkout --lightweight lp:magentoerpconnect magentoerpconnect
	echo ""
fi


# Install OpenERP
#################

echo "Installing OpenERP."
echo ""

cd /usr/local/src

# Install OpenERP server
echo "Installing OpenERP Server."
cd openerp-server
#~ Workaround for installation bug
python setup.py build
rsync -a bin/ build/lib.*/openerp-server/
python setup.py install
cd ..

# Install OpenERP Web client
echo "Installing OpenERP Web client."
cd openerp-web
easy_install -U openerp-web
cd ..

# Install OpenERP addons
echo "Installing OpenERP addons."
mkdir -p $addons_path
cp -r addons/* $addons_path

# Install OpenERP extra addons
if [[ "$install_extra_addons" == "y" ]]; then
	echo "Installing OpenERP extra addons."
	cp -r extra-addons/* $addons_path
fi

# Install OpenERP magentoerpconnect
if [[ "$install_magentoerpconnect" == "y" ]]; then
	echo "Installing OpenERP magentoerpconnect."
	cp -r magentoerpconnect $addons_path
fi

# Change permissions
echo "Changing permissions."
chown -R openerp.root $addons_path
chmod 755 $addons_path
# Permissions for Document Management Module: http://openobject.com/forum/topic13021.html?highlight=ftpchown openerp
chown openerp $install_path/lib/$python_rel/site-packages/openerp-server
# Log files
mkdir -p /var/log/openerp
touch /var/log/openerp/openerp.log
chown -R openerp.root /var/log/openerp/
mkdir -p /var/log/openerp-web
touch /var/log/openerp-web/access.log
touch /var/log/openerp-web/error.log
chown -R openerp.root /var/log/openerp-web/

# OpenERP Server init and config
echo "Making OpenERP Server init script"
cp /usr/local/share/libbash-ccorp/install-scripts/openerp-install/openerp-server_init.sh /etc/init.d/openerp-server
chmod +x /etc/init.d/openerp-server
sed -i "s#/usr/bin/openerp-server#$install_path/bin/openerp-server#g" /etc/init.d/openerp-server
echo ""

echo "Making OpenERP Server config script"
cp /usr/local/share/libbash-ccorp/install-scripts/openerp-install/openerp-server.conf /etc/openerp-server.conf
chmod 644 /etc/openerp-server.conf
sed -i "s/db_password =/db_password = $admin_passwd/g" /etc/openerp-server.conf
echo ""
update-rc.d openerp-server start 80 2 3 4 5 . stop 20 0 1 6 .

# OpenERP Web Client init and config
echo "Making OpenERP Web Client config file"
eval cp "$install_path/lib/$python_rel/dist-packages/openerp_web*.egg/config/openerp-web.cfg" /etc/openerp-web.cfg
#~ Activate log files
sed -i "s/#\?\(log.access_file.*\)/\1/g" /etc/openerp-web.cfg
sed -i "s/#\?\(log.error_file.*\)/\1/g" /etc/openerp-web.cfg
#~ Adds ClearCorp logo
sed -i "s/#\?\(company.url.*\)/company.url = \'http:\/\/www.clearcorp.co.cr\'/g" /etc/openerp-web.cfg
eval cp /usr/local/share/libbash-ccorp/install-scripts/openerp-install/company_logo.png "$install_path/lib/$python_rel/dist-packages/openerp_web*.egg/openerp/static/images/company_logo.png"
chown root.root /etc/openerp-web.cfg
chmod 644 /etc/openerp-web.cfg

echo "Making OpenERP Web Client init file"
eval cp "$install_path/lib/$python_rel/dist-packages/openerp_web*.egg/scripts/openerp-web" /etc/init.d/openerp-web
sed -i "s#/usr/bin/openerp-web#$install_path/bin/openerp-web#g" /etc/init.d/openerp-web
chmod +x /etc/init.d/openerp-web
update-rc.d openerp-web start 81 2 3 4 5 . stop 19 0 1 6 .

#~ ## Apache installation
#~ 
#~ #while [[ ! $install_apache =~ ^[YyNn]$ ]]; do
#~ #        read -p "Would you like to install apache (Y/n)? " -n 1 install_apache
#~ #        if [[ $install_apache == "" ]]; then
#~ #                install_apache="y"
#~ #        fi
#~ #        echo ""
#~ #done
#~ echo "Installing Apache"
#~ 
#~ apt-get -y install apache2
#~ 
#~ if [[ $dist == "hardy" ]]; then
	#~ 
	#~ cat > /tmp/default <<"EOF3"
#~ NameVirtualHost *:80
#~ <VirtualHost *:80>
        #~ ServerAdmin webmaster@localhost
        #~ ServerName openerpweb.com
        #~ #Redirect / https://openerpweb.com/
#~ 
        #~ DocumentRoot /var/www/
        #~ <Directory />
                #~ Options FollowSymLinks
                #~ AllowOverride None
        #~ </Directory>
        #~ <Directory /var/www/>
                #~ Options Indexes FollowSymLinks MultiViews
                #~ AllowOverride None
                #~ Order allow,deny
                #~ allow from all
        #~ </Directory>
#~ 
        #~ ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
        #~ <Directory "/usr/lib/cgi-bin">
                #~ AllowOverride None
                #~ Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
                #~ Order allow,deny
                #~ Allow from all
        #~ </Directory>
#~ 
        #~ ErrorLog /var/log/apache2/error.log
#~ 
        #~ # Possible values include: debug, info, notice, warn, error, crit,
        #~ # alert, emerg.
        #~ LogLevel warn
#~ 
        #~ CustomLog /var/log/apache2/access.log combined
        #~ ServerSignature On
#~ 
    #~ Alias /doc/ "/usr/share/doc/"
    #~ <Directory "/usr/share/doc/">
        #~ Options Indexes MultiViews FollowSymLinks
        #~ AllowOverride None
        #~ Order deny,allow
        #~ Deny from all
        #~ Allow from 127.0.0.0/255.0.0.0 ::1/128
    #~ </Directory>
#~ 
#~ </VirtualHost>
#~ EOF3
	#~ 
	#~ sudo cp /tmp/default /etc/apache2/sites-available/default
	#~ sudo chown root.root /etc/apache2/sites-available/default
	#~ sudo chmod 644 /etc/apache2/sites-available/default
	#~ 
	#~ cat > /tmp/default-ssl <<"EOF4"
#~ NameVirtualHost *:443
#~ <VirtualHost *:443>
	#~ ServerName openerpweb.com
        #~ ServerAdmin webmaster@localhost
	#~ SSLEngine on
	#~ SSLOptions +FakeBasicAuth +ExportCertData +StrictRequire	
	#~ SSLCertificateFile /etc/ssl/certs/ssl-cert-snakeoil.pem
	#~ SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key
                #~ 
	#~ <Proxy *>
	  #~ Order deny,allow
	  #~ Allow from all
	#~ </Proxy>
	#~ ProxyRequests Off
	#~ ProxyPass        /   http://127.0.0.1:8080/
	#~ ProxyPassReverse /   http://127.0.0.1:8080/
#~ 
        #~ RequestHeader set "X-Forwarded-Proto" "https"
#~ 
        #~ # Fix IE problem (http error 408/409)
        #~ SetEnv proxy-nokeepalive 1
#~ 
        #~ ErrorLog /var/log/apache2/error-ssl.log
        #~ # Possible values include: debug, info, notice, warn, error, crit,
        #~ # alert, emerg.
        #~ LogLevel warn
        #~ CustomLog /var/log/apache2/access-ssl.log combined
        #~ ServerSignature On
#~ </VirtualHost>
#~ EOF4
	#~ 
	#~ sudo cp /tmp/default-ssl /etc/apache2/sites-available/default-ssl
	#~ sudo chown root.root /etc/apache2/sites-available/default-ssl
	#~ sudo chmod 644 /etc/apache2/sites-available/default-ssl
	#~ 
	#~ echo "Making SSL certificate for Apache";
	#~ sudo /usr/sbin/make-ssl-cert generate-default-snakeoil --force-overwrite
	#~ # Snakeoil certificate files:
	#~ # /usr/share/ssl-cert/ssleay.cnf
	#~ # /etc/ssl/certs/ssl-cert-snakeoil.pem
	#~ # /etc/ssl/private/ssl-cert-snakeoil.key
	#~ 
	#~ echo "Enabling Apache Modules";
	#~ 
	#~ # Apache Modules:
	#~ sudo a2enmod ssl
	#~ # We enable default-ssl site after creating "/etc/apache2/sites-available/default-ssl" file (not available in Ubuntu8.04)
	#~ sudo a2ensite default-ssl
	#~ sudo a2enmod rewrite
	#~ sudo a2enmod suexec
	#~ sudo a2enmod include
	#~ sudo a2enmod proxy
	#~ sudo a2enmod proxy_http
	#~ sudo a2enmod proxy_connect
	#~ sudo a2enmod proxy_ftp
	#~ sudo a2enmod headers
	#~ 
	#~ #Add your server’s IP address and URL in /etc/hosts:
	#~ #    $ sudo vi /etc/hosts
	#~ #Replace
	#~ #    127.0.0.1 localhost
	#~ #    127.0.0.1 yourhostname yourhostnamealias
	#~ #With
	#~ #
	#~ #    127.0.0.1 localhost
	#~ #    192.168.x.x openerpweb.com yourhostname yourhostnamealias
	#~ sudo sed -i "s/\(^127\.0\.1\.1[[:space:]]*\)\([[:alnum:]].*\)/#\0\n$ipaddrvar $url \2/g" /etc/hosts
	#~ sudo sed -i "s/openerpweb\.com/$url/g" /etc/apache2/sites-available/default
	#~ sudo sed -i "s/openerpweb\.com/$url/g" /etc/apache2/sites-available/default-ssl
#~ elif [[ $dist == "karmic" ]]; then
	#~ a2enmod ssl
	#~ a2ensite default-ssl
	#~ a2enmod rewrite
	#~ a2enmod suexec
	#~ a2enmod include
	#~ a2enmod proxy
	#~ a2enmod proxy_http
	#~ a2enmod proxy_connect
	#~ a2enmod proxy_ftp
	#~ 
	#~ sudo sed -i "s/\(^ServerRoot.*\)/\1\nServerName localhost/g" /etc/apache2/apache2.conf
	#~ #Forcing Apache to redirect HTTP traffic to HTTPS
	#~ #sudo sed -i "s/\(ServerAdmin.*\)/\1\nServerName $url\nRedirect \/ https:\/\/$url\//g" /etc/apache2/sites-available/default
	#~ sudo sed -i "s/\(ServerAdmin.*\)/\1\nServerName $url\n\<Proxy \*\>\nOrder deny,allow\nAllow from all\n\<\/Proxy\>\nProxyRequests Off\nProxyPass        \/   http:\/\/127.0.0.1:8080\/\nProxyPassReverse \/   http:\/\/127.0.0.1:8080\/\nSetEnv proxy-nokeepalive 1/g" /etc/apache2/sites-available/default-ssl
	#~ sudo sed -i "s/\(^127\.0\.1\.1[[:space:]]*\)\([[:alnum:]].*\)/#\0\n$ipaddrvar $url \2/g" /etc/hosts
#~ fi
#~ 
#~ 
#~ echo "Restarting Apache";
#~ /etc/init.d/apache2 restart
#~ 
#~ TODO: Add shorewall support in ubuntu-server-install, and add rules here
#~ 
#~ echo "Starting openerp-server and openerp-web services"
#~ /etc/init.d/openerp-server start
#~ /etc/init.d/openerp-web start
#~ 
#~ 
#~ echo "Installing Postgre Web Administrator (phppgadmin)"
#~ apt-get install phppgadmin
#~ exit 0
