#       mkmenus-ccorp-main.sh
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

if [[ $1 == "5.0" ]] | [[ $1 == "6.0" ]]; then
	echo "This server will use $1 branch."
	branch=$1
elif
	# Source installation variables
	if [ -d /etc/openerp/5.0 ] && [ ! -d /etc/openerp/6.0 ]; then
		branch="5"
	elif [ ! -d /etc/openerp/5.0 ] && [ -d /etc/openerp/6.0 ]; then
		branch="6"
	else
		branch=""
		while [[ ! $branch =~ ^[56]$ ]]; do
			read -p "You have installed versions 5 and 6, choose the version for this server (5/_6_): " branch
			if [[ $branch == "" ]]; then
				branch="6"
			fi
			echo ""
		done
	fi

	if [[ $branch =~ ^[5]$ ]]; then
		echo "This server will use 5.0 branch."
		branch="5.0"
	else
		echo "This server will use 6.0 branch."
		branch="6.0"
	fi
fi

. /etc/openerp/$branch/install.cfg

if [[ `id -u` != `id -u $openerp_user` ]]; then
	echo "ccorp-openerp-mkmenus must be run as $openerp_user"
	exit 1
fi

if [[ ! -d $LIBBASH_CCORP_DIR ]]; then
	echo "libbash-ccorp not installed."
	exit 1
fi

mkdir -p /home/$openerp_user/.config/menus
mkdir -p /home/$openerp_user/.local/share/desktop-directories
mkdir -p /home/$openerp_user/.local/share/applications

if [[ ! -f /home/$openerp_user/.config/menus/applications.menu ]]; then
	cat << EOF >> /home/$openerp_user/.config/menus/applications.menu
<!DOCTYPE Menu
  PUBLIC '-//freedesktop//DTD Menu 1.0//EN'
  'http://standards.freedesktop.org/menu-spec/menu-1.0.dtd'>
<Menu>
	<Name>Applications</Name>
	<MergeFile type="parent">/etc/xdg/menus/applications.menu</MergeFile>
</Menu>
EOF
fi
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
			<Name>openerp-main-controls</Name>
			<Directory>openerp-main-controls.directory</Directory>
			<Include>
EOF

cat << EOF >> /home/$openerp_user/.local/share/desktop-directories/openerp-main-controls.directory
#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Directory
Icon=$LIBBASH_CCORP_DIR/install-scripts/openerp-install/icons/ccorp-logo.png
Name=openerp-main-controls
EOF

for i in "all" "apache" "postgresql"; do
	for j in "start" "stop" "restart"; do
		echo "				<Filename>openerp-$i-$j.desktop</Filename>" >>  /home/$openerp_user/.config/menus/applications.menu
		cat << EOF >> /home/$openerp_user/.local/share/applications/openerp-$i-$j.desktop
#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Icon=$LIBBASH_CCORP_DIR/install-scripts/openerp-install/icons/$i-$j.png
Name=$j $i
Exec=$LIBBASH_CCORP_DIR/install-scripts/openerp-install/openerp-dev-control.sh $i $j
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
