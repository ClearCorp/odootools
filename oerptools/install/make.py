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

import os, logging
from bzrlib.branch import Branch

#import shutil
#import tarfile
#import stat

_logger = logging.getLogger('oerptools.install.make')

def make_installer():

    _logger.info("Starting OERPTools make process")

    #TODO: enable the user to choose the oerptools path
    _logger.debug("Getting this oerptools dir absolute path")
    #TODO: Remove one ../ when moving oerptools to the root.
    scripts_path =  os.path.abspath(os.path.dirname(__file__)+'../../..')
    
    _logger.debug("Opening this bzr branch")
    this_branch = Branch.open(scripts_path)
    
    
    
    
    

    _logger.debug("Checking if previous binaries exist")
    if os.path.exists(scripts_path+"/bin"):
        _logger.info("Binaries (bin dir) exists, removing")
        shutil.rmtree(scripts_path+"/bin")

    _logger.debug("Making new bin dirs")
    os.makedirs(scripts_path+"/bin/oerptools_lib")
    os.makedirs(scripts_path+"/bin/oerptools_install")

    _logger.debug("Copying files to bin dirs")
    shutil.copy(context['oerptools_path']+"/lib/tools.py",
                context['oerptools_path']+"/bin/oerptools_lib/tools.py")
    shutil.copy(context['oerptools_path']+"/install/setup.py",
                context['oerptools_path']+"/bin/setup.py")
    shutil.copy(context['oerptools_path']+"/install/update.py",
                context['oerptools_path']+"/bin/oerptools_install/update.py")
    
    _logger.debug("Creating __init__ files into bin dirs")
    init_file = open(context['oerptools_path']+"/bin/oerptools_lib/__init__.py",'w')
    init_file.close()
    init_file = open(context['oerptools_path']+"/bin/oerptools_install/__init__.py",'w')
    init_file.close()

    _logger.debug("Setting setup.py as executable")
    os.chmod(context['oerptools_path']+"/bin/setup.py", stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    _logger.debug("Copying the created bin dir to oerptools-setup dir")
    if os.path.exists("oerptools-setup"):
        _logger.debug("oerptools-setup dir exists, removing")
        shutil.rmtree("oerptools-setup")
    shutil.copytree(context['oerptools_path']+"/bin", "oerptools-setup")
    shutil.copystat(context['oerptools_path']+"/bin", "oerptools-setup")

    _logger.debug("Compressing the oerptools-setup dir")
    tar = tarfile.open("oerptools-setup.tgz", "w:gz")
    tar.add("oerptools-setup")
    tar.close()

    _logger.debug("Deleting the oerptools-setup dir")
    shutil.rmtree("oerptools-setup")
    
    _logger.debug("Removing binaries")
    if os.path.exists(context['oerptools_path']+"/bin"):
        shutil.rmtree(context['oerptools_path']+"/bin")
    
    _logger.info("OERPTools make process finished")
    return
