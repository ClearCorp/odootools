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

import os
import platform
import subprocess
import sys
import logging

_logger = logging.getLogger('oerptools.lib.tools')

from oerptools.lib import config.params

def check_root():
    uid = os.getuid()
    return uid == 0

def exit_if_not_root():
    if not check_root():
        sys.stderr.write("The command: \"%s\" must be used as root. Aborting.\n" % command)
        sys.exit(1)
    else:
        return True

def get_os():
    os_name = platform.system()
    if os_name == "Linux":
        return {'os': 'Linux', 'version': platform.linux_distribution()}
    elif os_name == "Mac":
        return {'os': 'Mac', 'version': platform.mac_ver()}
    elif os_name == "Windows":
        return {'os': 'Windows', 'version': platform.win32_ver()}
    return False

def regenerate_ssh_keys():
    regen_script = open('/etc/regen-ssh-keys.sh', 'w')
    regen_script.write('''
#!/bin/bash
rm -f /etc/ssh/ssh_host_*
ssh-keygen -f /etc/ssh/ssh_host_rsa_key -t rsa -N ''
ssh-keygen -f /etc/ssh/ssh_host_dsa_key -t dsa -N ''

sed '/regen-ssh-keys.sh/d' /etc/rc.local > /etc/rc.local.tmp
cat /etc/rc.local.tmp > /etc/rc.local
rm -f /etc/rc.local.tmp

rm -f \$0
''')
    regen_script.close()
    os.chmod('/etc/regen-ssh-keys.sh', stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    rc_local = open('/etc/rc.local', 'a')
    rc_local.write('/etc/regen-ssh-keys.sh\n')
    rc_local.close()

def exec_command(command, as_root=False):
    if as_root:
        exit_if_not_root()
    process = subprocess.Popen(command,
                                shell=True,
                                stdin=sys.stdin.fileno(),
                                stdout=sys.stdout.fileno(),
                                stderr=sys.stderr.fileno())
    process.wait()
    return process

def command_not_available():
    _logger('The command %s is not implemented yet.' % config.params['command'])
    return
