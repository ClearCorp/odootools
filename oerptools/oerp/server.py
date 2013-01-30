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

import logging
_logger = logging.getLogger('oerptools.oerp.install')

import os, datetime, pwd

from oerptools.lib import config, bzr, tools

class oerpServer(object):
    
    def install(self):
        _logger.info('OpenERP server installation started.')
        
        _logger.debug('Checking if user is root')
        tools.exit_if_not_root('oerptools-install')
        
        os_info = tools.get_os()
        #Old Ubuntu versions have a suffix in postgresql init script
        posgresql_init_suffix = ''
        if os_info['os'] == 'Linux' and os_info['version'][0] == 'Ubuntu':
            if os_info['version'][1] in ('10.04','10.10'):
                postgresql_init_suffix = '-8.4'
        
        _logger.info('Please check the following information before continuing.')
        _logger.info('=========================================================')
        
        _logger.info('')
        _logger.info('System info')
        #Check system variables
        hostname = tools.get_hostname()
        _logger.info('Hostname: %s' % hostname[0])
        if not hostname[1]:
            _logger.warning('FQDN unknown, he hostname may not be properly set.')
        else:
            _logger.info('FQDN: %s' % hostname[1])
        
        _logger.info('Time and date: %s' % datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S (%Z)'))
        #TODO: list installed and default locale
        
        _logger.info('')
        _logger.info('Installation info')
        
        if config.params['intallation_type'] == 'dev':
            _logger.info('Installation type: development station')
        elif config.params['installation_type'] == 'server':
            _logger.info('Installation type: production server')
            if not 'user' in config.params:
                user = pwd.getpwuid(os.getuid()).pw_name
                _logger.warning('No user specified for dev intallation, using current user: %s' % user)
            else:
                _logger.info('User: %s' % config.params['user'])
                user = config.params['user']
        else:
            _logger.error('Installation type unknown: %s' % config.params['installation_type'])
            return False
        
        if config.params['install_openobject_addons']:
            
        
        
        
        
    
        return True

oerp_server = oerpServer()
