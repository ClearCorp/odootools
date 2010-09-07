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

if [[ ! -d $LIBBASH_CCORP_DIR ]]; then
	echo "libbash-ccorp not installed."
	exit 1
fi

#~ Libraries import
. $LIBBASH_CCORP_DIR/main-lib/checkRoot.sh

function bzrUpdate {
	bzr update $LIBBASH_CCORP_DIR

	# Check user is root
	checkRoot
	if [ -h /usr/local/sbin/ccorp-openerp-install ]; then
		rm /usr/local/sbin/ccorp-openerp-install
	fi
	ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-install/openerp-install.sh /usr/local/sbin/ccorp-openerp-install
	
	if [ -h /usr/local/sbin/ccorp-openerp-uninstall ]; then
		rm /usr/local/sbin/ccorp-openerp-uninstall
	fi
	ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-install/openerp-uninstall.sh /usr/local/sbin/ccorp-openerp-uninstall
	
	if [ -h /usr/local/sbin/ccorp-openerp-update ]; then
		rm /usr/local/sbin/ccorp-openerp-update
	fi
	ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-install/openerp-update.sh /usr/local/sbin/ccorp-openerp-update

	if [ -h /usr/local/sbin/ccorp-openerp-mkserver ]; then
		rm /usr/local/sbin/ccorp-openerp-mkserver
	fi
	ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-install/mkserver.sh /usr/local/sbin/ccorp-openerp-mkserver

	if [ -h /usr/local/sbin/ccorp-openerp-mkmenus ]; then
		rm /usr/local/sbin/ccorp-openerp-mkmenus
	fi
	ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-install/mkmenus.sh /usr/local/sbin/ccorp-openerp-mkmenus

	if [ -h /usr/local/sbin/ccorp-openerp-cp-db ]; then
		rm /usr/local/sbin/ccorp-openerp-cp-db
	fi
	ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-install/test-db/openerp-test-db.sh /usr/local/sbin/ccorp-openerp-cp-db

	if [ -h /usr/local/sbin/ccorp-ubuntu-server-install ]; then
		rm /usr/local/sbin/ccorp-ubuntu-server-install
	fi
	ln -s $LIBBASH_CCORP_DIR/install-scripts/ubuntu-server-install/ubuntu-server-install.sh /usr/local/sbin/ccorp-ubuntu-server-install

	if [ -h /usr/local/sbin/ccorp-bzr-make ]; then
		rm /usr/local/sbin/ccorp-bzr-make
	fi
	ln -s $LIBBASH_CCORP_DIR/install-scripts/bzr-install/bzr-make.sh /usr/local/sbin/ccorp-bzr-make

	if [ -h /usr/local/sbin/ccorp-bzr-update ]; then
		rm /usr/local/sbin/ccorp-bzr-update
	fi
	ln -s $LIBBASH_CCORP_DIR/install-scripts/bzr-install/bzr-update.sh /usr/local/sbin/ccorp-bzr-update

	if [ -h /usr/local/sbin/ccorp-users-server-install ]; then
		rm /usr/local/sbin/ccorp-users-server-install
	fi
	ln -s $LIBBASH_CCORP_DIR/install-scripts/users-server-install/users-server-install.sh /usr/local/sbin/ccorp-users-server-install

	if [ -h /usr/local/sbin/ccorp-koo-install ]; then
		rm /usr/local/sbin/ccorp-koo-install
	fi
	ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-dev-station/koo-install.sh /usr/local/sbin/ccorp-koo-install

	if [ -h /usr/local/sbin/ccorp-install-fonts ]; then
		rm /usr/local/sbin/ccorp-install-fonts
	fi
	ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-dev-station/install-fonts.sh /usr/local/sbin/ccorp-install-fonts
	
	return 0
}

bzrUpdate
