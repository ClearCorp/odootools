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
Description: Makes the odootools installer in a tgz
WARNING:    If you update this file, please remake the installer and
            upload it to launchpad.
            To make the installer, run this file or call oerptools-install-make
            if the oerptools are installed.
'''

import os, logging, shutil, tarfile, random, string
import odootools.lib.config
import odootools.lib.logger
from odootools.lib import bzr

_logger = logging.getLogger('odootools.install.make')


def make_installer():
    
    # Import and initialize bzr
    bzr.bzr_initialize()
    from bzrlib.branch import Branch
    
    params = odootools.lib.config.params
    
    _logger.info("Starting Odoo Tools make process")
    
    _logger.debug("Getting this odootools dir absolute path")
    scripts_path =  os.path.abspath(os.path.dirname(__file__)+'../../..')
    
    _logger.debug("Opening this bzr branch: %s" % scripts_path)
    this_branch = Branch.open(scripts_path)
    
    if 'target' in params:
        target_path = params['target']
    else:
        target_path = '.'
    target_path = os.path.abspath(target_path)
    tmp_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
    build_path = target_path+'/.odootools.'+tmp_string
    
    if not os.path.isdir(target_path):
        _logger.error('The provided directory path to build the installer (%s) doesn\'t exist. Exiting.' % target_path)
        return False
    
    if os.path.isdir(build_path):
        _logger.error('The temporary directory path used to build the installer (%s) already exist. Exiting.' % build_path)
        return False
    
    _logger.debug('Branching this branch to target branch: %s' % build_path)
    target_branch = this_branch.bzrdir.sprout(build_path).open_branch()
    
    # TODO: lp:1133410 Let the user choose the parent branch.
    #parent_path = 'lp:oerptools/2.0' #TODO rename parent branch
    parent_path = 'lp:~gs.clearcorp/oerptools/3.0_oerptools'
    _logger.debug('Set parent location for target branch: %s' % parent_path)
    target_branch.set_parent(parent_path)
    _logger.debug('Updating target branch from parent location.')
    parent_branch = Branch.open(parent_path)
    target_branch.pull(parent_branch)

    _logger.debug("Copying setup file to main dir.")
    shutil.copy(build_path+"/odootools/install/setup",
                build_path+"/setup")
    _logger.debug("Copying INSTALL.txt file to main dir.")
    shutil.copy(build_path+"/odootools/install/INSTALL.txt",
                build_path+"/INSTALL.txt")

    _logger.debug("Compressing the odootools dir")
    tar = tarfile.open(target_path+"/odootools-setup.tgz", "w:gz")
    tar.add(build_path, arcname='odootools')
    tar.close()

    _logger.debug("Deleting the odootools dir")
    shutil.rmtree(build_path)
    
    _logger.info("Odoo Tools make process finished")
    return
