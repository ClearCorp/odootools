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

import sys
import os
import shutil
import tarfile
import logging
import stat

def make_installer(context={}):
    # TODO: get logger
    logger = logging.getLogger(__name__)

    logger.info("test")

    # Get the scripts dir absolute path
    if not 'oerptools_path' in context:
        context.update({'oerptools_path' : os.path.abspath(os.path.dirname(__file__)+'../..')})

    # Remove previous binaries
    if os.path.exists(context['oerptools_path']+"/bin"):
        shutil.rmtree(context['oerptools_path']+"/bin")

    # Create new bin dirs
    os.makedirs(context['oerptools_path']+"/bin/oerptools_lib")
    os.makedirs(context['oerptools_path']+"/bin/oerptools_install")

    # Copy files to bin dirs
    shutil.copy(context['oerptools_path']+"/lib/tools.py",
                context['oerptools_path']+"/bin/oerptools_lib/tools.py")
    shutil.copy(context['oerptools_path']+"/install/setup.py",
                context['oerptools_path']+"/bin/setup.py")
    shutil.copy(context['oerptools_path']+"/install/update.py",
                context['oerptools_path']+"/bin/oerptools_install/update.py")
    
    init_file = open(context['oerptools_path']+"/bin/oerptools_lib/__init__.py",'w')
    init_file.close()
    init_file = open(context['oerptools_path']+"/bin/oerptools_install/__init__.py",'w')
    init_file.close()

    # Set setup.py as executable
    os.chmod(context['oerptools_path']+"/bin/setup.py", stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # Copy the created bin dir to openerp-ccorp-scripts dir
    if os.path.exists("oerptools-setup"):
        shutil.rmtree("oerptools-setup")
    shutil.copytree(context['oerptools_path']+"/bin", "oerptools-setup")
    shutil.copystat(context['oerptools_path']+"/bin", "oerptools-setup")

    # Compress the openerp-ccorp-scripts dir
    tar = tarfile.open("oerptools-setup.tgz", "w:gz")
    tar.add("oerptools-setup")
    tar.close()

    # Delete the openerp-ccorp-scripts dir
    shutil.rmtree("oerptools-setup")
    return
