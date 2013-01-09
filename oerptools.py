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

import sys, os, logging

_logger = logging.getLogger('oerptools')

# Add the module oerptools to PYTHONPATH
# This is necesary in order to call the module without installing it
oerptools_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(oerptools_path+'/..')

from oerptools.lib import config, logger

if __name__ == '__main__':
    
    # Read configuration values
    params = config.params
    
    # Init logger
    logger.init_loggers()
    
    _logger.debug('Params loaded, logger initialized.')
    
    params['function']()
    
    _logger.info('OERPTools finished.')
