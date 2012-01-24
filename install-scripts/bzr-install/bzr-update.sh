#       bzr-update.sh
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

if [[ ! -d $OPENERP_CCORP_DIR ]]; then
	echo "openerp-ccorp-scripts not installed."
	exit 1
fi

#~ Libraries import
. $OPENERP_CCORP_DIR/main-lib/checkRoot.sh

# Settings import
if [[ ! -f /etc/openerp-ccorp-scripts/settings.cfg ]]; then
	mkdir -p /etc/openerp-ccorp-scripts
	cat > /etc/openerp-ccorp-scripts/settings.cfg <<EOF
repo="lp:openerp-ccorp-scripts"
branch=stable
EOF
fi
. /etc/openerp-ccorp-scripts/settings.cfg

function bzrUpdate {
	# Make sure parent branch is updated
	cd $OPENERP_CCORP_DIR
	bzr pull ${repo}/${branch}

	# Check user is root
	checkRoot
	for x in $(ls -1 $OPENERP_CCORP_DIR/bin-links); do
		rm -r /usr/local/sbin/$x
		ln -s $OPENERP_CCORP_DIR/bin-links/$x /usr/local/sbin/$x
	done
	
	return 0
}

bzrUpdate
