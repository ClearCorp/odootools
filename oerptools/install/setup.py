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

import os, sys, logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
log_file = logging.FileHandler('setup.log')
log_file.setLevel(logging.DEBUG)
# create console handler with a higher log level
log_console = logging.StreamHandler()
log_console.setLevel(logging.INFO)
# create formatter and add it to the handlers
log_file_formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s: %(message)s')
log_console_formatter = logging.Formatter('%(levelname)s - %(name)s: %(message)s')
log_file.setFormatter(log_file_formatter)
log_console.setFormatter(log_console_formatter)
# add the handlers to the logger
logger.addHandler(log_file)
logger.addHandler(log_console)

def setup():
    # Set the pythonpath to include the required libs
    _oerptools_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(_oerptools_path)

    from oerptools_lib import tools
    from oerptools_install import update

    tools.exit_if_not_root()
    
    logger.warning('test')
    
    

    def bzr_install():
        os_version = tools.get_os()
        if os_version['os'] == 'Linux':
            if os_version['version'][0] == 'Ubuntu':
                return ubuntu_bzr_install()
            elif os_version['version'][0] == 'arch':
                return arch_bzr_install()
        return False

    def ubuntu_bzr_install():
        #TODO: logger gets the output of the command
        print('Installing bzr...')
        print('')
        tools.exec_command('apt-get -y update')
        tools.exec_command('apt-get -y install bzr python-bzrlib')
        return

    def arch_bzr_install():
        #TODO: logger gets the output of the command
        print('Installing bzr...')
        print('')
        tools.exec_command('pacman -Sy --noconfirm bzr')
        return

    def oerptools_install(install_dir):
        os_version = tools.get_os()
        if os_version['os'] == 'Linux':
            if os_version['version'][0] == 'Ubuntu':
                return ubuntu_oerptools_install(install_dir)
            elif os_version['version'][0] == 'arch':
                return arch_oerptools_install(install_dir)
        return False

    def ubuntu_oerptools_install(install_dir):
        import re
        from bzrlib.branch import Branch
        from bzrlib.plugin import load_plugins
        
        #TODO: logger gets the output of the command
        print('Installing oerptools...')
        print('')
        
        f = open('/etc/environment')
        environment = f.read()
        f.close()
        if 'OERPTOOLS_DIR' in environment:
            environment = re.sub(r'OERPTOOLS_DIR.*','OERPTOOLS_DIR=%s' % install_dir, environment)
            f = open('/etc/environment','w+')
            f.write(environment)
        else:
            f = open('/etc/environment','a+')
            f.write('OERPTOOLS_DIR=%s\n' % install_dir)
        f.close()
        
        if os.path.isdir(install_dir):
            print('bzr repository: %s already exists.' % install_dir)
            print('Updating...')
            branch = Branch.open(install_dir)
            branch.pull(branch.get_parent())
        else:
            #TODO: add the option for the user to install another version of oerptools
            #the prefered method of selection is with a command line option.
            
            #Make config directory
            if not os.path.exists('/etc/oerptools'):
                os.mkdir('/etc/oerptools')
            
            #Get the branch
            # Load the bzr plugins - the "launchpad" plugin provides support for the "lp:" shortcut
            load_plugins()
            remote_branch = Branch.open('lp:openerp-ccorp-scripts/stable')
            branch = remote_branch.bzrdir.sprout(install_dir).open_branch()
        
        tools.exec_command('')

        return
        
    '''


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
            #    read -p "Do you want to install openerp-ccorp-scripts stable or trunk (S/t)? " -n 1
            #    if [[ $REPLY == "" ]]; then
            #        REPLY="s"
            #    fi
            #    echo ""
            #done
            #if [[ $REPLY =~ ^[Ss]$ ]]; then
            #    branch=stable
            #else
            #    branch=trunk
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

    def arch_oerptools_install(install_dir):
        #TODO: logger gets the output of the command
        print('Installing bzr...')
        print('')
        tools.exec_command('pacman -Sy --noconfirm bzr')
        return
    
    # TODO: Give the option to the user to choose the installation dir
    install_dir = "/usr/local/share/oerptools"
    
    print("Bzr and openerp-ccorp-scripts installation script")
    print('')
    
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
        #TODO: Change raw_input to input for python3
        reply = raw_input('Do you want to install bzr (Y/n)? ')
        if reply == '':
            reply = 'y'
        print('')
    
    if reply.lower() in ('y', 'yes'):
        bzr_install()
        print('')
    
    # Setup bzr repository
    reply = ''
    while not reply.lower() in ('y', 'yes', 'n', 'no'):
        reply = raw_input('Do you want to install oerptools (Y/n)? ')
        if reply == '':
            reply = 'y'
        print('')
    
    if reply.lower() in ('y', 'yes'):
        oerptools_install(install_dir)
        print('')
    
    


if __name__ == '__main__':
    setup()
