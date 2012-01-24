#       openerp-uninstall.sh
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
. $OPENERP_CCORP_DIR/main-lib/getDist.sh
. $OPENERP_CCORP_DIR/openerp-scripts/openerp-lib.sh

# Check user is root
checkRoot

# Print title
echo "OpenERP uninstallation script"
echo "-----------------------------"
echo ""

# Set distribution
dist=""
getDist dist
echo "Distribution: $dist"
echo ""

openerp_get_dist

for i in $(ls /etc/init.d/openerp*); do
	echo "$i stop"
	$i stop
	echo "rm /etc/init.d/$i"
	rm $i
	echo "update-rc.d `basename $i` remove"
	update-rc.d `basename $i` remove
done
echo "rm -r /etc/openerp/$branch"
rm -r /etc/openerp/$branch
echo "rm -r /var/log/openerp"
rm -r /var/log/openerp
echo "rm -r /var/run/openerp"
rm -r /var/run/openerp
echo "rm -r $install_path/openerp-*"
rm -r $install_path/openerp-*
echo "rm -r $base_path/bin/openerp-*"
rm -r $base_path/bin/openerp-*
echo "rm -r $base_path/share/man/man1/openerp*"
rm -r $base_path/share/man/man1/openerp*
echo "rm -r $base_path/share/man/man5/openerp*"
rm -r $base_path/share/man/man5/openerp*

exit 0
