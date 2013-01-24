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
Description: Makes the oerptools installer in a tgz
WARNING:    If you update this file, please remake the installer and
            upload it to launchpad.
            To make the installer, run this file or call oerptools-install-make
            if the oerptools are installed.
'''

import os, logging, shutil, tarfile, random, string
import oerptools.lib.config
import oerptools.lib.logger
from oerptools.lib import bzr

_logger = logging.getLogger('oerptools.install.make')


def make_installer():

    # Import and initialize bzr
    bzr.bzr_initialize()
    from bzrlib.branch import Branch
    
    params = oerptools.lib.config.params
    
    _logger.info("Starting OERPTools make process")
    
    #TODO: enable the user to choose the oerptools path
    _logger.debug("Getting this oerptools dir absolute path")
    #TODO: Remove one ../ when moving oerptools to the root.
    scripts_path =  os.path.abspath(os.path.dirname(__file__)+'../../..')
    
    _logger.debug("Opening this bzr branch: %s" % scripts_path)
    this_branch = Branch.open(scripts_path)
    
    if 'target' in params:
        target_path = params['target']
    else:
        target_path = '.'
    target_path = os.path.abspath(target_path)
    tmp_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
    build_path = target_path+'/.oerptools.'+tmp_string
    
    if not os.path.isdir(target_path):
        _logger.error('The provided directory path to build the installer (%s) doesn\'t exist. Exiting.' % target_path)
        return False
    
    if os.path.isdir(build_path):
        _logger.error('The temporary directory path used to build the installer (%s) already exist. Exiting.' % build_path)
        return False
    
    _logger.debug('Branching this branch to target branch: %s' % build_path)
    target_branch = this_branch.bzrdir.sprout(build_path).open_branch()
    
    # TODO: Let the user choose the parent branch.
    parent_path = 'lp:oerptools/2.0'
    _logger.debug('Set parent location for target branch: %s' % parent_path)
    target_branch.set_parent(parent_path)
    _logger.debug('Updating target branch from parent location.')
    parent_branch = Branch.open(parent_path)
    target_branch.pull(parent_branch)

    _logger.debug("Copying setup file to main dir.")
    shutil.copy(build_path+"/oerptools/install/setup",
                build_path+"/setup")
    _logger.debug("Copying INSTALL.txt file to main dir.")
    shutil.copy(build_path+"/oerptools/install/INSTALL.txt",
                build_path+"/INSTALL.txt")

    _logger.debug("Compressing the oerptools dir")
    tar = tarfile.open(target_path+"/oerptools-setup.tgz", "w:gz")
    tar.add(build_path, arcname='oerptools')
    tar.close()

    _logger.debug("Deleting the oerptools dir")
    shutil.rmtree(build_path)
    
    _logger.info("OERPTools make process finished")
    return
