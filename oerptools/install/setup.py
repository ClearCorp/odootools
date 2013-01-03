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
Description: Setup bzr and gets a branch of oerptools
WARNING:     If you update this file, please remake the installer and
             upload it to launchpad.
             To make the installer, call oerptools-build command.
'''

import os, sys

def setup():
    _oerptools_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(_oerptools_path)

    from oerptools_lib import tools
    from oerptools_install import update

    tools.exit_if_not_root()
    
    # TODO: Give the option to the user to choose the installation dir
    install_dir = "/usr/local/share/oerptools"
    
    print("Bzr and openerp-ccorp-scripts installation script")
    print()
    
    os_version = tools.get_os()
    if os_version['os'] == 'Linux':
        dist = os_version['version'][0]
        print("Detected OS: %s (%s)" % (dist,os_version['os']))
    else:
        dist = os_version['os']
        print("Detected OS: %s" % dist)
    
    # Install bzr
    reply = ''
    
    while not reply.lower() in ('y', 'yes', 'n', 'no'):
        reply = input('Do you want to install bzr (Y/n)? ')
        if reply == '':
            reply = 'y'
        print()
    
    
    
    '''


if [[ $REPLY =~ ^[Yy]$ ]]; then
	echo "Installing bzr..."
	echo ""
	apt-get -y update
	apt-get -y install bzr
fi
echo ""

# Setup bzr repository
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to install openerp-ccorp-scripts (Y/n)? " -n 1
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	echo "Installing openerp-ccorp-scripts..."
	echo ""
	if [ $(cat /etc/environment | grep -c OPENERP_CCORP_DIR) == 0 ]; then
		echo 'OPENERP_CCORP_DIR="/usr/local/share/openerp-ccorp-scripts"' >> /etc/environment
	else
		sed -i "s#OPENERP_CCORP_DIR.*#OPENERP_CCORP_DIR=\"/usr/local/share/openerp-ccorp-scripts\"#g" /etc/environment
	fi
	dir=$(pwd)
	if [ -d /usr/local/share/openerp-ccorp-scripts ]; then
		echo "bzr repository: /usr/local/share/openerp-ccorp-scripts already exists."
		echo "Updating..."
		cd /usr/local/share/openerp-ccorp-scripts
		bzr pull
	else
		# Removed the choice, the trunk isn't updated anymore, only install from stable
		#------------------------------------------------------------------------------
		#Chose the branch to install
		#REPLY='none'
		#while [[ ! $REPLY =~ ^[SsTt]$ ]]; do
		#	read -p "Do you want to install openerp-ccorp-scripts stable or trunk (S/t)? " -n 1
		#	if [[ $REPLY == "" ]]; then
		#		REPLY="s"
		#	fi
		#	echo ""
		#done
		#if [[ $REPLY =~ ^[Ss]$ ]]; then
		#	branch=stable
		#else
		#	branch=trunk
		#fi

		branch=stable

		mkdir -p /etc/openerp-ccorp-scripts
		bzr branch lp:openerp-ccorp-scripts/${branch} /usr/local/share/openerp-ccorp-scripts
		cat > /etc/openerp-ccorp-scripts/settings.cfg <<EOF
repo="lp:openerp-ccorp-scripts"
branch=$branch
EOF
	fi
	cd $dir
	. ccorp-openerp-scripts-update.sh
	echo "If this is the first time you are running this script, please run 'export OPENERP_CCORP_DIR=/usr/local/share/openerp-ccorp-scripts'"
fi
echo ""
'''

if __name__ == '__main__':
    setup()
