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

# Check user is root
checkRoot

rm /usr/local/sbin/ccorp-openerp-install
ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-install/openerp-install.sh /usr/local/sbin/ccorp-openerp-install
rm /usr/local/sbin/ccorp-openerp-mkserver
ln -s $LIBBASH_CCORP_DIR/install-scripts/openerp-install/mkserver.sh /usr/local/sbin/ccorp-openerp-mkserver
rm /usr/local/sbin/ccorp-ubuntu-server-install
ln -s $LIBBASH_CCORP_DIR/install-scripts/ubuntu-server-install/ubuntu-server-install.sh /usr/local/sbin/ccorp-ubuntu-server-install
rm /usr/local/sbin/ccorp-bzr-make
ln -s $LIBBASH_CCORP_DIR/install-scripts/bzr-install/bzr-make.sh /usr/local/sbin/ccorp-bzr-make
rm /usr/local/sbin/ccorp-bzr-update
ln -s $LIBBASH_CCORP_DIR/install-scripts/bzr-install/bzr-update.sh /usr/local/sbin/ccorp-bzr-update
rm /usr/local/sbin/ccorp-users-server-install
ln -s $LIBBASH_CCORP_DIR/install-scripts/users-server-install/users-server-install.sh /usr/local/sbin/users-server-install

bzr update $LIBBASH_CCORP_DIR
