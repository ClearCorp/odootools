#!/bin/bash

echo "OpenERP installation script."
echo ""

source checkRoot.sh
checkRoot

OS_804=`awk '/Ubuntu 8.04.3 LTS/ {print $0}' /etc/issue`
OS_910=`awk '/Ubuntu 9.10/ {print $0}' /etc/issue`
if [ -z "$OS_804" -a -z "$OS_910" ]; then
	echo "This program must be executed on Ubuntu 8.04.3 LTS or Ubuntu 9.10 (Desktop or Server)"
	exit 1
fi
if [ -n "$OS_804" ]; then
	# Ubuntu 8.04, python 2.5
	posgresql_rel=8.3
	python_rel=python2.5
	ubuntu_rel=8.04
	install_path=/usr
	addons_path=$install_path/lib/$python_rel/site-packages/openerp-server/addons/
else
	# Ubuntu 9.10, python 2.6
	posgresql_rel=8.4
	python_rel=python2.6
	ubuntu_rel=9.10
	install_path=/usr/local
	addons_path=$install_path/lib/$python_rel/dist-packages/openerp-server/addons/
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
	./prepare-rs-machine.sh
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

#Set the admin password
admin_passwd=""
while [[ $admin_passwd == "" ]]; do
        read -p "Enter the OpenERP administrator password: " admin_passwd
        if [[ $admin_passwd == "" ]]; then
                echo "The password cannot be empty."
	else
		read -p "Enter the OpenERP administrator password: " admin_passwd2
		echo ""
		if [[ $admin_passwd == $admin_passwd2 ]]; then
			echo "OpenERP administrator password set."
		else
			admin_passwd=""
			echo "Passwords don't match."
		fi
        fi
        echo ""
done


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
apt-get -y install python python-psycopg2 python-reportlab python-egenix-mxdatetime python-tz python-pychart python-pydot python-lxml python-libxslt1 python-vobject python-imaging python-dev build-essential python-setuptools
echo ""

# Install bazaar.
echo "Installing bazaar."
apt-get -y install bzr
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
	sudo -u postgres psql template1 -U postgres -c "alter user openerp with password '$admin_passwd'"
fi


# Downloading OpenERP
#####################

echo "Downloading OpenERP."
echo ""

cd /usr/local/src

# Download openerp-server latest stable/trunk release.
echo "Downloading openerp-server latest stable/trunk release."
bzr branch lp:openobject-server/$branch openerp-server
echo ""

# Download openerp-client-web latest stable release.
echo "Downloading openerp-client-web latest stable release."
bzr branch lp:openobject-client-web/$branch openerp-web
echo ""

# Download openerp addons latest stable/trunk branch.
echo "Downloading openerp addons latest stable/trunk branch."
bzr branch lp:openobject-addons/$branch addons
echo ""

# Download extra addons
if [[ $install_extra_addons =~ ^[Yy]$ ]]; then
	echo "Downloading extra addons"
	bzr branch lp:openobject-addons/extra-$branch extra-addons
	echo ""
fi

# Download magentoerpconnect
if [[ $install_magentoerpconnect =~ ^[Yy]$ ]]; then
	echo "Downloading magentoerpconnect."
	bzr branch lp:magentoerpconnect magentoerpconnect
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

# Make OpenERP init file
echo "Making OpenERP init file"

cat > /etc/init.d/openerp-server <<"EOF"
#!/bin/sh

### BEGIN INIT INFO
# Provides:		openerp-server
# Required-Start:	$syslog
# Required-Stop:	$syslog
# Should-Start:		$network
# Should-Stop:		$network
# Default-Start:	2 3 4 5
# Default-Stop:		0 1 6
# Short-Description:	Enterprise Resource Management software
# Description:		OpenERP is a complete ERP and CRM software.
### END INIT INFO

PATH=/sbin:/bin:/usr/sbin:/usr/bin
DAEMON=/usr/bin/openerp-server
NAME=openerp-server
DESC=openerp-server
USER=openerp

test -x ${DAEMON} || exit 0

set -e

case "${1}" in
	start)
		echo -n "Starting ${DESC}: "

		start-stop-daemon --start --quiet --pidfile /var/run/${NAME}.pid \
			--chuid ${USER} --background --make-pidfile \
			--exec ${DAEMON} -- --config=/etc/openerp-server.conf

		echo "${NAME}."
		;;

	stop)
		echo -n "Stopping ${DESC}: "

		start-stop-daemon --stop --quiet --pidfile /var/run/${NAME}.pid \
			--oknodo

		echo "${NAME}."
		;;

	restart|force-reload)
		echo -n "Restarting ${DESC}: "

		start-stop-daemon --stop --quiet --pidfile /var/run/${NAME}.pid \
			--oknodo

		sleep 1

		start-stop-daemon --start --quiet --pidfile /var/run/${NAME}.pid \
			--chuid ${USER} --background --make-pidfile \
			--exec ${DAEMON} -- --config=/etc/openerp-server.conf

		echo "${NAME}."
		;;

	*)
		N=/etc/init.d/${NAME}
		echo "Usage: ${NAME} {start|stop|restart|force-reload}" >&2
		exit 1
		;;
esac

exit 0

EOF
chmod +x /etc/init.d/openerp-server
sed -i "s#/usr/bin/openerp-server#$install_path/bin/openerp-server#g" /etc/init.d/openerp-server

# Make OpenERP init file
echo "Making OpenERP config file"

cat > /etc/openerp-server.conf <<"EOF2"
# /etc/openerp-server.conf(5) - configuration file for openerp-server(1)

[options]
# Enable the debugging mode (default False).
#verbose = True 

# The file where the server pid will be stored (default False).
#pidfile = /var/run/openerp.pid

# The file where the server log will be stored (default False).
logfile = /var/log/openerp/openerp.log

# The IP address on which the server will bind.
# If empty, it will bind on all interfaces (default empty).
#interface = localhost
interface = 
# The TCP port on which the server will listen (default 8069).
port = 8069

# Enable debug mode (default False).
#debug_mode = True 

# Launch server over https instead of http (default False).
secure = False

# Specify the SMTP server for sending email (default localhost).
smtp_server = mail.clearcorp.co.cr

# Specify the SMTP user for sending email (default False).
smtp_user = relay@clearcorp.co.cr

# Specify the SMTP password for sending email (default False).
smtp_password = passwd

# Specify the database name.
db_name =

# Specify the database user name (default None).
db_user = openerp

# Specify the database password for db_user (default None).
db_password = 

# Specify the database host (default localhost).
db_host = localhost

# Specify the database port (default None).
db_port = 5432

EOF2
chown root.root /etc/openerp-server.conf
chmod 644 /etc/openerp-server.conf
sed -i "s/db_password =/db_password = $admin_passwd/g" /etc/openerp-server.conf

cat > /etc/init.d/openerp-web <<"EOF7"
#!/bin/sh

### BEGIN INIT INFO
# Provides:             openerp-web
# Required-Start:       $syslog
# Required-Stop:        $syslog
# Should-Start:         $network
# Should-Stop:          $network
# Default-Start:        2 3 4 5
# Default-Stop:         0 1 6
# Short-Description:    OpenERP Web - the Web Client of the OpenERP
# Description:          OpenERP is a complete ERP and CRM software.
### END INIT INFO

PATH=/sbin:/bin:/usr/sbin:/usr/bin
DAEMON=/usr/bin/openerp-web
NAME=openerp-web
DESC=openerp-web

# Specify the user name (Default: openerp).
USER="openerp"

# Specify an alternate config file (Default: /etc/openerp-web.conf).
CONFIGFILE="/etc/openerp-web.conf"

# pidfile
PIDFILE=/var/run/$NAME.pid

# Additional options that are passed to the Daemon.
DAEMON_OPTS="-c $CONFIGFILE"

[ -x $DAEMON ] || exit 0
[ -f $CONFIGFILE ] || exit 0

checkpid() {
    [ -f $PIDFILE ] || return 1
    pid=`cat $PIDFILE`
    [ -d /proc/$pid ] && return 0
    return 1
}

if [ -f /lib/lsb/init-functions ] || [ -f /etc/gentoo-release ] ; then

    do_start() {
        start-stop-daemon --start --quiet --pidfile $PIDFILE \
            --chuid $USER  --background --make-pidfile \
            --exec $DAEMON -- $DAEMON_OPTS
        
        RETVAL=$?
        sleep 5         # wait for few seconds

        return $RETVAL
    }

    do_stop() {
        start-stop-daemon --stop --quiet --pidfile $PIDFILE --oknodo

        RETVAL=$?
        sleep 2         # wait for few seconds
        rm -f $PIDFILE  # remove pidfile

        return $RETVAL
    }

    do_restart() {
        start-stop-daemon --stop --quiet --pidfile $PIDFILE --oknodo

        sleep 2         # wait for few seconds
        rm -f $PIDFILE  # remove pidfile

        start-stop-daemon --start --quiet --pidfile $PIDFILE \
            --chuid $USER --background --make-pidfile \
            --exec $DAEMON -- $DAEMON_OPTS

        RETVAL=$?
        sleep 5         # wait for few seconds

        return $RETVAL
    }

else
    
    do_start() {
        $DAEMON $DAEMON_OPTS > /dev/null 2>&1 &
        
        RETVAL=$?
        sleep 5         # wait for few seconds

        echo $! > $PIDFILE  # create pidfile

        return $RETVAL
    }

    do_stop() {

        pid=`cat $PIDFILE`
        kill -15 $pid

        RETVAL=$?
        sleep 2         # wait for few seconds
        rm -f $PIDFILE  # remove pidfile

        return $RETVAL
    }

    do_restart() {

        if [ -f $PIDFILE ]; then
            do_stop
        fi

        do_start

        return $?
    }

fi

start_daemon() {

    if [ -f $PIDFILE ]; then
        echo "pidfile already exists: $PIDFILE"
        exit 1
    fi

    echo -n "Starting $DESC: "

    do_start

    checkpid

    if [ $? -eq 1 ]; then                
        rm -f $PIDFILE
        echo "failed."
        exit 1
    fi

    echo "done."
}

stop_daemon() {

    checkpid

    if [ $? -eq 1 ]; then
        exit 0
    fi

    echo -n "Stopping $DESC: "

    do_stop

    if [ $? -eq 1 ]; then
        echo "failed."
        exit 1
    fi

    echo "done."
}

restart_daemon() {

    echo -n "Reloading $DESC: "

    do_restart

    checkpid

    if [ $? -eq 1 ]; then                
        rm -f $PIDFILE
        echo "failed."
        exit 1
    fi

    echo "done."
}

status_daemon() {

    echo -n "Checking $DESC: "

    checkpid

    if [ $? -eq 1 ]; then
        echo "stopped."
    else
        echo "running."
    fi
}

case "$1" in
    start) start_daemon ;;
    stop) stop_daemon ;;
    restart|force-reload) restart_daemon ;;
    status) status_daemon ;;
    *)
        N=/etc/init.d/$NAME
        echo "Usage: $N {start|stop|restart|force-reload|status}" >&2
        exit 1
        ;;
esac

exit 0
EOF7


chmod +x /etc/init.d/openerp-web
sed -i "s#/usr/bin/openerp-web#$install_path/bin/openerp-web#g" /etc/init.d/openerp-web


cat > /etc/openerp-web.conf <<"EOF8"
[global]

# Some server parameters that you may want to tweak
server.socket_host = "0.0.0.0"
server.socket_port = 8080

# Sets the number of threads the server uses
server.thread_pool = 20

server.environment = "production"

# Simple code profiling
server.profile_on = False
server.profile_dir = "profile"

# if this is part of a larger site, you can set the path
# to the TurboGears instance here
#server.webpath = ""

# Set to True if you are deploying your App behind a proxy
# e.g. Apache using mod_proxy
tools.proxy.on = False

# If your proxy does not add the X-Forwarded-Host header, set
# the following to the *public* host url.
#tools.proxy.base = 'http://mydomain.com'

# logging
#log.access_file = "/var/log/openerp-web/access.log"
log.error_file = "/var/log/openerp-web/error.log"

# OpenERP Server
[openerp]
host = 'localhost'
port = '8070'
protocol = 'socket'

# Web client settings
[openerp-web]
# filter dblists based on url pattern?
# NONE: No Filter
# EXACT: Exact Hostname
# UNDERSCORE: Hostname_
# BOTH: Exact Hostname or Hostname_

dblist.filter = 'NONE'

# whether to show Databases button on Login screen or not
dbbutton.visible = True

# will be applied on company logo
company.url = ''

# options to limit data rows in M2M/O2M lists, will be overriden 
# with limit="5", min_rows="5" attributes in the tree view definitions
child.listgrid.limit = 5
child.listgrid.min_rows = 5
EOF8

chown root.root /etc/openerp-web.conf
chmod 644 /etc/openerp-web.conf

update-rc.d openerp-server start 21 2 3 4 5 . stop 21 0 1 6 .
update-rc.d openerp-web start 70 2 3 4 5 . stop 20 0 1 6 .


