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
Description: Installs OERPTools
WARNING:    If you update this file, please remake the installer and
            upload it to launchpad.
            To make the installer, run this file or call oerptools-build
            if the oerptools are installed.
'''

import logging
from oerptools.lib import config, tools, bzr

_logger = logging.getLogger('oerptools.install.install')


def install():
    _logger.debug('Checking if user is root')
    tools.exit_if_not_root('oerptools-install')
    
    _logger.debug('Installing bzr')
    bzr.bzr_install()
    
    
    def oerptools_install(install_dir):
        os_version = tools.get_os()
        if os_version['os'] == 'Linux':
            if os_version['version'][0] == 'Ubuntu':
                return ubuntu_oerptools_install(install_dir)
            elif os_version['version'][0] == 'arch':
                return arch_oerptools_install(install_dir)
        _logger.warning('Can\'t install OERPTools in this OS')
        return False
    
    def ubuntu_oerptools_install(install_dir):
        import re
        
        # Initialize bzr
        bzr.bzr_initialize()
        
        _logger.info('Installing oerptools')
        
        f = open('/etc/environment')
        environment = f.read()
        f.close()
        if 'OERPTOOLS_DIR' in environment:
            environment = re.sub(r'OERPTOOLS_DIR.*','OERPTOOLS_DIR=%s' % (install_dir, environment))
            f = open('/etc/environment','w+')
            f.write(environment)
        else:
            f = open('/etc/environment','a+')
            f.write('OERPTOOLS_DIR=%s\n' % install_dir)
        f.close()
        
        if os.path.isdir(install_dir):
            bzr.info('bzr repository: %s already exists, updating.' % install_dir)
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
            remote_branch = Branch.open('lp:oerptools')
            branch = remote_branch.bzrdir.sprout(install_dir).open_branch()
        
        # Update config
        if os.path.isfile(install_dir):
            
        
        tools.exec_command('')

        return
        
    '''
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
