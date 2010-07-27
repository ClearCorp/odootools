#!/bin/bash

function proc_ctl {
	gksudo service $1 $2
}

case $2 in
server)
	case $3 in
	start)
		proc_ctl openerp-server-$1 start
		;;
	stop)
		proc_ctl openerp-server-$1 stop
		;;
	restart)
		proc_ctl openerp-server-$1 restart
		;;
	esac
	;;
web)
	case $3 in
	start)
		proc_ctl openerp-web-$1 start
		;;
	stop)
		proc_ctl openerp-web-$1 stop
		;;
	restart)
		proc_ctl openerp-web-$1 restart
		;;
	esac
	;;
all)
	case $3 in
	start)
		proc_ctl openerp-server-$1 start
		proc_ctl openerp-web-$1 start
		;;
	stop)
		proc_ctl openerp-server-$1 stop
		proc_ctl openerp-web-$1 stop
		;;
	restart)
		proc_ctl openerp-server-$1 restart
		proc_ctl openerp-web-$1 restart
		;;
	esac
	;;
apache)
	case $2 in
	start)
		proc_ctl apache2 start
		;;
	stop)
		proc_ctl apache2 stop
		;;
	restart)
		proc_ctl apache2 restart
		;;
	esac
	;;
postgresql)
	case $2 in
	start)
		proc_ctl postgresql-8.4 start
		;;
	stop)
		proc_ctl postgresql-8.4 stop
		;;
	restart)
		proc_ctl postgresql-8.4 restart
		;;
	esac
	;;
esac
