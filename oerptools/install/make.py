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

logger = logging.getLogger(__name__)

logger.info("test")

# Get the scripts dir absolute path
scripts_dir = os.path.abspath(os.path.dirname(sys.argv[0])+"/../..")

# Remove previous binaries
if os.path.exists(scripts_dir+"/bin"):
    shutil.rmtree(scripts_dir+"/bin")

# Create new bin dirs
os.makedirs(scripts_dir+"/bin/lib")
os.makedirs(scripts_dir+"/bin/install")

# Copy files to bin dirs
shutil.copy(scripts_dir+"/lib/checkRoot.sh",
            scripts_dir+"/bin/lib/checkRoot.sh")
shutil.copy(scripts_dir+"/lib/getDist.sh",
            scripts_dir+"/bin/lib/getDist.sh")
shutil.copy(scripts_dir+"/lib/setSources.sh",
            scripts_dir+"/bin/lib/setSources.sh")

shutil.copy(scripts_dir+"/install/ccorp-openerp-scripts-setup.sh",
            scripts_dir+"/bin/install-scripts/ccorp-openerp-scripts-install/ccorp-openerp-scripts-setup.sh")
shutil.copy(scripts_dir+"/install-scripts/ccorp-openerp-scripts-install/ccorp-openerp-scripts-update.sh",
            scripts_dir+"/bin/install-scripts/ccorp-openerp-scripts-install/ccorp-openerp-scripts-update.")

shutil.copy(scripts_dir+"/install-scripts/ccorp-openerp-scripts-install/setup.sh",
            scripts_dir+"/bin/setup.sh")

# Set setup.py as executable
os.chmod(scripts_dir+"/bin/setup.sh", stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

# Copy the created bin dir to openerp-ccorp-scripts dir
shutil.copytree(scripts_dir+"/bin", "openerp-ccorp-scripts")
shutil.copystat(scripts_dir+"/bin", "openerp-ccorp-scripts")

# Compress the openerp-ccorp-scripts dir
tar = tarfile.open("openerp-ccorp-scripts.tgz", "w:gz")
tar.add("openerp-ccorp-scripts")
tar.close()

# Delete the openerp-ccorp-scripts dir
shutil.rmtree("openerp-ccorp-scripts")
