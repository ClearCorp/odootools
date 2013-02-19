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
_logger = logging.getLogger('oerptools.oerp.instance')

import os

from oerptools.lib import config, bzr, tools

class oerpInstance(object):
    def __init__(self):
        os_info = tools.get_os()
        #Old Ubuntu versions have a suffix in postgresql init script
        self._postgresql_init_suffix = ''
        self._postgresql_version = ''
        if os_info['os'] == 'Linux' and os_info['version'][0] == 'Ubuntu':
            if os_info['version'][1] in ('10.04','10.10'):
                self._postgresql_init_suffix = '-8.4'
            if os_info['version'][1] < '11.10':
                self._postgresql_version = '8.4'
            else:
                self._postgresql_version = '9.1'
        
        self._branch = config.params['branch'] or '7.0'
        self._installation_type = config.params[branch+'_installation_type'] or config.params['installation_type'] or'dev'
        self._user = config.params[branch+'_user'] or config.params['user'] or None
        self._install_openobject_addons = config.params[branch+'_install_openobject_addons'] or config.params['install_openobject_addons'] or True
        self._install_openerp_ccorp_addons = config.params[branch+'_install_openerp_ccorp_addons'] or config.params['install_openerp_ccorp_addons'] or True
        self._install_openerp_costa_rica = config.params[branch+'_install_openerp_costa_rica'] or config.params['install_openerp_costa_rica'] or True
        self._admin_password = config.params[branch+'_admin_password'] or config.params['admin_password'] or None
        self._postgresql_password = config.params[branch+'_postgresql_password'] or config.params['postgresql_password'] or None
        return super(oerpInstance, self).__init__()
    
    
