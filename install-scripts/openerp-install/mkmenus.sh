#       mkmenus.sh
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

if [[ $1 == "" ]]; then
	echo "Usage ccorp-openerp-mkmenus <server-name>"
	exit 1
fi

openerp_user=$(cat /etc/openerp/user)
if [[ `id -u` != `id -u $openerp_user` ]]; then
	echo "ccorp-openerp-mkmenus must be run as $openerp_user"
	exit 1
fi

if [[ ! -d $LIBBASH_CCORP_DIR ]]; then
	echo "libbash-ccorp not installed."
	exit 1
fi

#~ Libraries import
. $LIBBASH_CCORP_DIR/main-lib/getDist.sh

# Init log file
INSTALL_LOG_PATH=/var/log/openerp
INSTALL_LOG_FILE=$INSTALL_LOG_PATH/install.log

if [[ ! -f $INSTALL_LOG_FILE ]]; then
	mkdir -p $INSTALL_LOG_PATH
	touch $INSTALL_LOG_FILE
fi

function log {
	echo "$(date): $1" >> $INSTALL_LOG_FILE
}
function log_echo {
	echo $1
	log "$1"
}
log ""

log_echo "Making developer menus..."
#~ Delete all empty lines
sed '/^$/d' /home/$openerp_user/.config/menus/applications.menu
#~ Delete last line
sed '$d' < /home/$openerp_user/.config/menus/applications.menu > /home/$openerp_user/.config/menus/applications.menu2
mv /home/$openerp_user/.config/menus/applications.menu2 /home/$openerp_user/.config/menus/applications.menu
#~ Adds new lines
cat << EOF >> /home/$openerp_user/.config/menus/applications.menu
	<Menu>
		<Name>Development</Name>
		<Menu>
			<Name>openerp-ccorp-addons</Name>
			<Directory>openerp-ccorp-addons.directory</Directory>
			<Include>
EOF

cat << EOF >> /home/$openerp_user/.local/share/desktop-directories/openerp-$1.desktop
#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Directory
Icon=$LIBBASH_CCORP_DIR/main-lib/ccorp-favicon.png
Name=openerp-$1
EOF

for i in "server" "web" "all"; do
	for j in "start" "stop" "restart"; do
		echo "				<Filename>openerp-$1-$i-$j.desktop</Filename>" >>  /home/$openerp_user/.config/menus/applications.menu
		cat << EOF >> /home/$openerp_user/.local/share/applications/openerp-$1-$i-$j.desktop
#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Icon=$LIBBASH_CCORP_DIR/main-lib/ccorp-favicon.png
Name=$j $i openerp-$1
Exec=\$LIBBASH_CCORP_DIR/install-scripts/openerp-install/openerp-dev-control.sh $1 $i $j
EOF
	done
done
cat << EOF >> /home/$openerp_user/.config/menus/applications.menu
			</Include>
		</Menu>
	</Menu>
</Menu>
EOF

exit 0
