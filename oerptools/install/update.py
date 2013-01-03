#!/usr/bin/python2
# -*- coding: utf-8 -*-
########################################################################
#
#  OpenERP Tools by CLEARCORP S.A.
#  Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public
#  License along with this program.  If not, see 
#  <http://www.gnu.org/licenses/>.
#
########################################################################

'''
Description: Updates the oerptools installation
WARNING:    If you update this file, please remake the installer and
            upload it to launchpad.
            To make the installer, run this file or call oerptools-install-make
            if the oerptools are installed.
'''



'''
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
repo="http://bazaar.launchpad.net/openerp-ccorp-scripts"
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
		if [[ -e /usr/local/sbin/$x ]]; then
			rm -r /usr/local/sbin/$x
		fi
		ln -s $OPENERP_CCORP_DIR/bin-links/$x /usr/local/sbin/$x
	done
	
	return 0
}

bzrUpdate
'''
