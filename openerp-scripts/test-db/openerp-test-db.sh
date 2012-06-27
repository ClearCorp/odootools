#!/bin/bash

#       openerp-test-db.sh
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

if [[ ! -d $OPENERP_CCORP_DIR ]]; then
	echo "openerp-ccorp-scripts not installed."
	exit 1
fi

#~ Libraries import
. $OPENERP_CCORP_DIR/main-lib/checkRoot.sh
# Check user is root
checkRoot

# $1: original db
# $2: copy db
# $3: copy server name

# Stop copy server
/etc/init.d/openerp-server-$3 stop
server_name=openerp_$3
proc_name=${server_name:0:15}
if [[ `ps -A | grep -c $proc_name` -gt 0 ]]; then
	killall -s KILL openerp_$3
fi

# Re-create the database
sudo -u postgres psql -c "DROP DATABASE $2"
sudo -u postgres psql -c "CREATE DATABASE $2"

# Close connections do copy db
sudo -u postgres psql -c "SELECT procpid FROM pg_stat_activity where datname='$2'" | grep -e "[0-9]$" | while read line; do kill $line; kill -s KILL $line; done

# Copy database
sudo -u postgres pg_dump --format=c --no-owner $1 | sudo -u postgres pg_restore --no-owner --dbname=$2

# Restart copy server
/etc/init.d/openerp-server-$3 start
sudo -u postgres psql -c "ALTER DATABASE $2 OWNER TO openerp_$3"

exit 0
