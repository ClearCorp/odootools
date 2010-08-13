#!/bin/bash

function proc_ctl {
	gksudo service $1 $2
}

case $1 in
all)
	case $2 in
	start)
		gksu -w -D "OpenERP ALL start: Apache start" service apache2 start
		gksu -w -D "OpenERP ALL start: PostgreSQL start" postgresql-8.4 start
		for i in $(ls /etc/init.d/openerp-*); do
			gksu -w -D "OpenERP ALL start: $i" $i start
		done
		;;
	stop)
		gksu -w -D "OpenERP ALL stop: Apache stop" service apache2 stop
		gksu -w -D "OpenERP ALL stop: PostgreSQL stop" service postgresql-8.4 stop
		for i in $(ls /etc/init.d/openerp-*); do
			gksu -w -D "OpenERP ALL stop: $i" $i stop
		done
		;;
	restart)
		gksu -w -D "OpenERP ALL restart: Apache restart" service apache2 restart
		gksu -w -D "OpenERP ALL restart: PostgreSQL restart" service postgresql-8.4 restart
		for i in $(ls /etc/init.d/openerp-*); do
			gksu -w -D "OpenERP ALL restart: $i" $i restart
		done
		;;
	esac
	;;
apache)
	case $2 in
	start)
		gksu -w -D "Apache start" service apache2 start
		;;
	stop)
		gksu -w -D "Apache stop" service apache2 stop
		;;
	restart)
		gksu -w -D "Apache restart" service apache2 restart
		;;
	esac
	;;
postgresql)
	case $2 in
	start)
		gksu -w -D "PostgreSQL start" service postgresql-8.4 start
		;;
	stop)
		gksu -w -D "PostgreSQL stop" service postgresql-8.4 stop
		;;
	restart)
		gksu -w -D "PostgreSQL restart" service postgresql-8.4 restart
		;;
	esac
	;;
*)
	case $2 in
	server)
		case $3 in
		start)
			gksu -w -D "openerp-server-$1 start: PostgreSQL start" service postgresql-8.4 start
			gksu -w -D "openerp-server-$1 start" service openerp-server-$1 start
			;;
		stop)
			gksu -w -D "openerp-server-$1 stop" service openerp-server-$1 stop
			;;
		restart)
			gksu -w -D "openerp-server-$1 restart: PostgreSQL start" service postgresql-8.4 start
			gksu -w -D "openerp-server-$1 restart" service openerp-server-$1 restart
			;;
		esac
		;;
	web)
		case $3 in
		start)
			gksu -w -D "openerp-web-$1 start: Apache start" service apache2 start
			gksu -w -D "openerp-web-$1 start" service openerp-web-$1 start
			;;
		stop)
			gksu -w -D "openerp-web-$1 stop" service openerp-web-$1 stop
			;;
		restart)
			gksu -w -D "Aopenerp-web-$1 start: pache start" service apache2 start
			gksu -w -D "openerp-web-$1 restart" service openerp-web-$1 restart
			;;
		esac
		;;
	all)
		case $3 in
		start)
			gksu -w -D "openerp-all-$1 start: PostgreSQL start" service postgresql-8.4 start
			gksu -w -D "openerp-all-$1 start: Apache start" service apache2 start
			gksu -w -D "openerp-all-$1 start: server" service openerp-server-$1 start
			gksu -w -D "openerp-all-$1 start: web" service openerp-web-$1 start
			;;
		stop)
			gksu -w -D "openerp-all-$1 stop: server" service openerp-server-$1 stop
			gksu -w -D "openerp-all-$1 stop: web" service openerp-web-$1 stop
			;;
		restart)
			gksu -w -D "openerp-all-$1 restart: PostgreSQL start"  service postgresql-8.4 start
			gksu -w -D "openerp-all-$1 restart: Apache start" service apache2 start
			gksu -w -D "openerp-all-$1 restart: server" service openerp-server-$1 restart
			gksu -w -D "openerp-all-$1 restart: web" service openerp-web-$1 restart
			;;
		esac
		;;
	esac
	;;
esac

echo "Finished"
sleep 2
exit 0
