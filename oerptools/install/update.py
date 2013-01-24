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
Description: Updates the oerptools installation
WARNING:    If you update this file, please remake the installer and
            upload it to launchpad.
            To make the installer, run this file or call oerptools-install-make
            if the oerptools are installed.
'''

import logging
_logger = logging.getLogger('oerptools.install.update')

import os

from oerptools.lib import config, bzr

def update():
    _logger.debug('Checking if user is root')
    tools.exit_if_not_root('oerptools-update')
    
    bzr.bzr_initialize()
    
    if 'oerptools_path' in config.params:
        oerptools_path = config.params['oerptools_path']
    else:
        _logger.error('The OERPTools path was not specified. Exiting.')
        return False
    
    if not os.path.isdir(oerptools_path):
        _logger.error('The OERPTools path (%s) is not a valid directory. Exiting.' % oerptools_path)
        return False
        
    if 'source_branch' in config.params:
        bzr.bzr_pull(oerptools_path, config.params['source_branch'])
    else:
        bzr.bzr_pull(oerptools_path)
        
    return True
