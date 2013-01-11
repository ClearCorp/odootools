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
Description: Setup bzr and gets a branch of oerptools
WARNING:     If you update this file, please remake the installer and
             upload it to launchpad.
             To make the installer, call oerptools-build command.
'''

import os, sys, logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
log_file = logging.FileHandler('setup.log')
log_file.setLevel(logging.DEBUG)
# create console handler with a higher log level
log_console = logging.StreamHandler()
log_console.setLevel(logging.INFO)
# create formatter and add it to the handlers
log_file_formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s: %(message)s')
log_console_formatter = logging.Formatter('%(levelname)s - %(name)s: %(message)s')
log_file.setFormatter(log_file_formatter)
log_console.setFormatter(log_console_formatter)
# add the handlers to the logger
logger.addHandler(log_file)
logger.addHandler(log_console)

def setup():

    


    
    # TODO: Give the option to the user to choose the installation dir
    install_dir = "/usr/local/share/oerptools"
    
    print("Bzr and openerp-ccorp-scripts installation script")
    print('')
    
    os_version = tools.get_os()
    if os_version['os'] == 'Linux':
        dist = os_version['version'][0]
        print("Detected OS: %s (%s)" % (dist,os_version['os']))
    else:
        dist = os_version['os']
        print("Detected OS: %s" % dist)
    
    # Install bzr
    reply = ''
    while not reply.lower() in ('y', 'yes', 'n', 'no'):
        #TODO: Change raw_input to input for python3
        reply = raw_input('Do you want to install bzr (Y/n)? ')
        if reply == '':
            reply = 'y'
        print('')
    
    if reply.lower() in ('y', 'yes'):
        bzr_install()
        print('')
    
    # Setup bzr repository
    reply = ''
    while not reply.lower() in ('y', 'yes', 'n', 'no'):
        reply = raw_input('Do you want to install oerptools (Y/n)? ')
        if reply == '':
            reply = 'y'
        print('')
    
    if reply.lower() in ('y', 'yes'):
        oerptools_install(install_dir)
        print('')
    
    


if __name__ == '__main__':
    setup()
