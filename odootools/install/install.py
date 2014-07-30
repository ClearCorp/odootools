#!/usr/bin/python2
# -*- coding: utf-8 -*-
########################################################################
#
#  Odoo Tools by CLEARCORP S.A.
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
Description: Installs Odoo Tools
WARNING:    If you update this file, please remake the installer and
            upload it to launchpad.
            To make the installer, run this file or call odootools-build
            if the odootools are installed.
'''

import os, shutil, stat, logging
from odootools.lib import config, tools, bzr

_logger = logging.getLogger('oerptools.install.install')

def install():
    
    def odootools_install(install_dir):
        os_version = tools.get_os()
        if os_version['os'] == 'Linux':
            if (os_version['version'][0] == 'Ubuntu') or (os_version['version'][0] == 'LinuxMint'):
                return ubuntu_odootools_install(install_dir)
            elif os_version['version'][0] == 'arch':
                return arch_odootools_install(install_dir)
        _logger.warning('Can\'t install Odoo Tools in this OS')
        return False
    
    def ubuntu_odootools_install(install_dir):
        import re
        
        _logger.info('Installing odootools')
        
        # Initialize bzr
        bzr.bzr_initialize()
        from bzrlib.branch import Branch
        
        # Get this odootools branch directory
        branch_path = os.path.abspath(os.path.dirname(__file__)+"/../..")
        
        # Values dict to store default config values for this install
        values = {
            'main': {},
            'logging': {},
            }
        
        # Set odootools_path for new file
        values['main'].update({'odootools_path': install_dir})
        
        # Set config_file for new file
        if 'install_config_path' in config.params:
            values['main'].update({'config_file': config.params['install_config_path']})
        elif 'config_file' in config.params and config.params['config_file']:
            values['main'].update({'config_file': config.params['config_file'][-1]})
        else:
            values['main'].update({'config_file': '/etc/odootools/settings.conf'})
            
        # Set log_file for new file
        if 'log_file' in config.params:
            values['logging'].update({'log_file': config.params['log_file']})
        else:
            values['logging'].update({'log_file': '/var/log/odootools/odootools.log'})
            
        # Set log_handler for new file
        if 'log_handler' in config.params:
            values['logging'].update({'log_handler': ','.join(config.params['log_handler'])})
        else:
            values['logging'].update({'log_handler': ':INFO'})
        
        
        f = open('/etc/environment')
        environment = f.read()
        f.close()
        if 'ODOOTOOLS_DIR' in environment:
            environment = re.sub(r'ODOOTOOLS_DIR.*','ODOOTOOLS_DIR=%s' % install_dir, environment)
            f = open('/etc/environment','w+')
            f.write(environment)
        else:
            f = open('/etc/environment','a+')
            f.write('ODOOTOOLS_DIR=%s\n' % install_dir)
        f.close()
        
        if os.path.isdir(install_dir):
            _logger.info('bzr repository: %s already exists, updating.' % install_dir)
            bzr.bzr_pull(install_dir)
        else:
            # Copy this branch
            branch = bzr.bzr_branch(branch_path, install_dir)
            # Update from lp
            if 'source_branch' in config.params:
                try:
                    branch.set_parent(config.params['source_branch'])
                    bzr.bzr_pull(install_dir)
                except:
                    branch.set_parent('lp:oerptools')# TODO Update branch
                    bzr.bzr_pull(install_dir)
            else:
                branch.set_parent('lp:oerptools')
                bzr.bzr_pull(install_dir)
        
        #Make config directory
        if not os.path.exists('/etc/odootools'):
            os.mkdir('/etc/odootools')
        
        # Update config
        if not os.path.exists(values['main']['config_file']):
            shutil.copy(branch_path+"/odootools/install/default-odootools.conf",values['main']['config_file'])
        elif not os.path.isfile(values['main']['config_file']):
            _logger.warning('Config file (%s) not updated because it is not a regular file.' % values['main']['config_file'])
        
        config.params.update_config_file_values(values, update_file=values['main']['config_file'])
        
        # Make bin symlink to odootools.py
        if os.path.islink('/usr/local/bin/odootools'):
            os.remove('/usr/local/bin/odootools')
            os.symlink(install_dir+'/odootools.py','/usr/local/bin/odootools')
        elif os.path.exists('/usr/local/bin/odootools'):
            _logger.warning('/usr/local/bin/odootools already exists and is not a symlink.')
        else:
            os.symlink(install_dir+'/odootools.py','/usr/local/bin/odootools')
        
        # Create log dir
        log_file = os.path.abspath(values['logging']['log_file'])
        log_dir = os.path.dirname(log_file)
        if not os.path.isdir(log_dir) and os.path.exists(log_dir):
            _logger.warning('The log directory (%s) already exists but isn\'t a valid directory.' % log_dir)
        elif not os.path.isdir(log_dir):
            _logger.debug('Making the log directory: %s' % log_dir)
            os.makedirs(log_dir)
            os.chmod(log_dir, stat.S_IREAD | stat.S_IWRITE)
        else:
            os.chmod(log_dir, stat.S_IREAD | stat.S_IWRITE)

        return True
    
    def arch_odootools_install(install_dir):
        # No differences as of now
        return ubuntu_odootools_install(install_dir)


    _logger.debug('Checking if user is root')
    tools.exit_if_not_root('odootools-install')
    
    _logger.debug('Installing bzr')
    bzr.bzr_install()
        
    if 'install_target_path' in config.params:
        install_dir = config.params['install_target_path']
    else:
        install_dir = '/usr/local/share/odootools'
    
    odootools_install(install_dir)
    
    return True
