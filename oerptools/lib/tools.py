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

import oerptools.lib.config

def check_root():
    uid = os.getuid()
    _logger.debug('UID = %s' % uid)
    return uid == 0

def exit_if_not_root(command_name):
    if not check_root():
        _logger.error("The command: \"%s\" must be used as root. Aborting.\n" % command_name)
        sys.exit(1)
    else:
        return True

def get_os():
    """ Returns a dict with os info:
    key os: os name
    key version: tuple with more info
    """
    supported_dists = ['Ubuntu','arch']
    os_name = platform.system()
    os_version = ""
    known_os = False
    if os_name == "Linux":
        known_os = True
        # for linux the os_version is in the form: (distro name, version, version code name)
        os_version = platform.linux_distribution(supported_dists=supported_dists)
    elif os_name == "Mac":
        known_os = True
        # for mac the os_version is in the form: (release, versioninfo, machine)
        os_version = platform.mac_ver()
    elif os_name == "Windows":
        known_os = True
        os_version = platform.win32_ver()
    
    if known_os:
        _logger.debug('OS: %s, Version: %s' % (os_name, os_version))
        return {'os': os_name, 'version': os_version}
    else:
        return False

def get_hostname():
    import socket
    short_name = socket.gethostname()
    try:
        long_name = socket.gethostbyaddr(socket.gethostname())[0]
    except:
        long_name = None
    return (short_name, long_name)

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
    _logger.debug('Executing command: %s' % command)
    if as_root and not check_root():
        command = 'sudo ' + command
    process = subprocess.Popen(command,
                                shell=True,
                                stdin=sys.stdin.fileno(),
                                stdout=sys.stdout.fileno(),
                                stderr=sys.stderr.fileno())
    process.wait()
    _logger.debug('Command finished: %s' % process.returncode)
    return process.returncode

def command_not_available():
    _logger.error('The command %s is not implemented yet.' % oerptools.lib.config.params['command'])
    return
