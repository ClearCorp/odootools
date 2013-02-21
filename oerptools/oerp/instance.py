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
        self._name = config.params['name']
        self._installation_type = config.params[branch+'_installation_type'] or config.params['installation_type'] or'dev'
        self._user = config.params[branch+'_user'] or config.params['user'] or None
        self._install_openobject_addons = config.params[branch+'_install_openobject_addons'] or config.params['install_openobject_addons'] or True
        self._install_openerp_ccorp_addons = config.params[branch+'_install_openerp_ccorp_addons'] or config.params['install_openerp_ccorp_addons'] or True
        self._install_openerp_costa_rica = config.params[branch+'_install_openerp_costa_rica'] or config.params['install_openerp_costa_rica'] or True
        self._admin_password = config.params[branch+'_admin_password'] or config.params['admin_password'] or None
        self._postgresql_password = config.params[branch+'_postgresql_password'] or config.params['postgresql_password'] or None
        return super(oerpInstance, self).__init__()
    
    def make_addons_links(self):
        _logger.info('Creating symbolic links for %s' % self._name)
        


function mkserver_install_addons {
    if [[ $install_openerp_addons =~ ^[Yy]$ ]]; then mkserver_addons_mk_links openobject-addons; fi
    if [[ $install_ccorp_addons =~ ^[Yy]$ ]]; then mkserver_addons_mk_links openerp-ccorp-addons; fi
    if [[ $install_costa_rica_addons =~ ^[Yy]$ ]]; then mkserver_addons_mk_links openerp-costa-rica; fi
    if [[ $install_extra_addons =~ ^[Yy]$ ]]; then mkserver_addons_mk_links openobject-addons-extra; fi
    if [[ $install_magentoerpconnect =~ ^[Yy]$ ]]; then mkserver_addons_mk_links magentoerpconnect; fi
    if [[ $install_nantic =~ ^[Yy]$ ]]; then mkserver_addons_mk_links nantic; fi
}

function mkserver_addons_config {
    # Create config line for addons
    log_echo "Creating config addons settings line..."
    if [[ $branch == "6.1" ]] || [[ $branch == "trunk" ]]; then
        cd /srv/openerp/$branch/instances/$name/addons >> $INSTALL_LOG_FILE
        if [[ $addons_config == "" ]]; then
            addons_config="/srv/openerp/$branch/instances/$name/web/addons"
        else
            addons_config="$addons_config,/srv/openerp/$branch/instances/$name/web/addons"
        fi
        for x in $(ls -d *); do
            addons_config="$addons_config,/srv/openerp/$branch/instances/$name/addons/$x"
        done
    else
        if [[ $addons_config == "" ]]; then
            addons_config="/srv/openerp/$branch/instances/$name/addons"
        else
            addons_config="$addons_config,/srv/openerp/$branch/instances/$name/addons"
        fi
    fi
}
