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

if [[ ! -d $LIBBASH_CCORP_DIR ]]; then
	echo "libbash-ccorp not installed."
	exit 1
fi

#~ Libraries import
. $LIBBASH_CCORP_DIR/main-lib/checkRoot.sh
. $LIBBASH_CCORP_DIR/main-lib/getDist.sh

# Check user is root
checkRoot

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

openerp_user=$(cat /etc/openerp/user)

function mkmenus {
log_echo "Making developer menus..."
#~ Delete all empty lines
sed '/^$/d' /home/$openerp_user/.config/menus/application.menu
#~ Delete last line
sed '$d' /home/$openerp_user/.config/menus/application.menu
#~ Adds new lines
cat << EOF >> /home/$openerp_user/.config/menus/application.menu
	<Menu>
		<Name>Development</Name>
		<Menu>
			<Name>openerp-ccorp-addons</Name>
			<Directory>openerp-ccorp-addons.directory</Directory>
			<Include>
EOF

cat << EOF >> /home/$openerp_user/.local/share/desktop-directories/openerp-$name.desktop
#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Directory
Icon=$LIBBASH_CCORP_DIR/main-lib/ccorp-favicon.png
Name=openerp-$name
EOF

for i in "server" "web" "all"; do
	for j in "start" "stop" "restart"; do
		echo "				<Filename>openerp-$name-$i-$j.desktop</Filename>" >>  /home/$openerp_user/.local/share/desktop-directories/openerp-$name.desktop
		cat << EOF >> /home/$openerp_user/.local/share/applications/openerp-$name-$i-$j.desktop
#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Icon=$LIBBASH_CCORP_DIR/main-lib/ccorp-favicon.png
Name=$j $i openerp-$name
Exec="$LIBBASH_CCORP_DIR/install-scripts/openerp-install/openerp-dev-control.sh $name $i $j"
EOF
	done
done
cat << EOF >> /home/$openerp_user/.config/menus/application.menu
			</Include>
		</Menu>
	</Menu>
</Menu>
EOF
fi

return 0
}

sudo -u $openerp_user mkmenus $1
exit 0
