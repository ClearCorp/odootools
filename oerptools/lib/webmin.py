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

import os, sys
import subprocess
from oerptools.lib import tools

def webmin_install():
    os_version = tools.get_os()
    if os_version['os'] == 'Linux':
        if os_version['version'][0] == 'Ubuntu':
            return ubuntu_webmin_install()
        elif os_version['version'][0] == 'arch':
            return arch_webmin_install()
    return False

def ubuntu_webmin_install():
    if not os.path.isfile('/etc/apt/sources.list.d/webmin.list'):
        apt_src = open('/etc/apt/sources.list.d/webmin.list', 'w')
        apt_src.write('# Webmin repository')
        apt_src.write('deb http://download.webmin.com/download/repository sarge contrib')
        apt_src.close()
    command = subprocess.Popen(['wget -q http://www.webmin.com/jcameron-key.asc -O - | apt-key add -'],
                                shell=True,
                                stdin=sys.stdin.fileno(),
                                stdout=sys.stdout.fileno(),
                                stderr=sys.stderr.fileno())
    command.wait()
    #TODO: logger gets the output of the command
    return

def arch_webmin_install():
    command = subprocess.Popen('pacman -Sy',
                                shell=True,
                                stdin=sys.stdin.fileno(),
                                stdout=sys.stdout.fileno(),
                                stderr=sys.stderr.fileno())
    command.wait()
    #TODO: logger gets the output of the command

    command = subprocess.Popen('pacman -Sy webmin',
                                shell=True,
                                stdin=sys.stdin.fileno(),
                                stdout=sys.stdout.fileno(),
                                stderr=sys.stderr.fileno())
    command.wait()
    #TODO: logger gets the output of the command

