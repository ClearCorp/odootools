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

import os, re
import logging
from odootools.lib import config, git_lib, tools

_logger = logging.getLogger('odootools.dev.repository')

class repository(object):
    def __init__(self):
        _logger.info('Initializing Odoo development repository.')
        self._repo_dir = os.path.expanduser(config.params['repo_dir'] or '~/Development/odoo')
        self._push = config.params['push'] or False
        self._repo_exists = False
        return super(repository, self).__init__()
    
    def _branch_project(self, source, name, clearcorp=False, remote_project=''):
        _logger.info('Creating development repository for %s' % source)
        
        project_dir = os.path.abspath(self._repo_dir) + '/%s' % name
        
        if os.path.isdir(project_dir):
            _logger.warning('Repository in %s already exists, delete before running the script to recreate.' % name)
        else:
            if not git_lib.git_clone(source, project_dir):
                _logger.error('Failed to create repo in %s. Exiting.' % name)
                return False
            if clearcorp:
                _logger.info('Adding dev remote to branch')
                if not remote_project:
                    remote_project = name
                git_lib.git_add_remote(project_dir, 'dev', 'git@github.com:CLEARCORP-dev/' + remote_project)
        return True
    
    def _update_project(self, name):
        _logger.info('Updating development repository for %s' % name)
        
        project_dir = os.path.abspath(self._repo_dir) + '/%s' % name
        
        if not os.path.isdir(project_dir):
            _logger.error('Repository %s doesn\'t exists. Exiting.' % name)
            return False
        
        if not git_lib.git_fetch(project_dir):
            _logger.error('Updating Failed. Exiting.' % name)
            return False
        _logger.info('Updated development repository %s' % name)
        return True
    
    def make(self):
        _logger.info('Making new Odoo development repository.')
        
        _logger.info('Please inform github your ssh key before continue.')
        answer = False
        while not answer:
            answer = raw_input('Are you sure you want to continue (y/n)? ')
            if re.match(r'^y$|^yes$', answer, flags=re.IGNORECASE):
                answer = 'y'
            elif re.match(r'^n$|^no$', answer, flags=re.IGNORECASE):
                answer = 'n'
                _logger.error('Aborting. Please run odootools again whe ready.')
                return False
            else:
                answer = False
        
        # TODO: show progress
        _logger.info('Cloning odoo source.')
        self._branch_project('git@github.com:odoo/odoo','odoo')
        _logger.info('Cloning odoo source finished.')
        _logger.info('Cloning odoo CLEARCORP fork source.')
        self._branch_project('git@github.com:CLEARCORP/odoo','odoo-fork', clearcorp=True, remote_project='odoo')
        _logger.info('Cloning odoo CLEARCORP fork finished.')
        _logger.info('Cloning odoo-clearcorp source.')
        self._branch_project('git@github.com:CLEARCORP/odoo-clearcorp','odoo-clearcorp', clearcorp=True)
        _logger.info('Cloning odoo-clearcorp finished.')
        _logger.info('Cloning odoo-costa-rica source.')
        self._branch_project('git@github.com:CLEARCORP/odoo-costa-rica','odoo-costa-rica', clearcorp=True)
        _logger.info('Cloning odoo-costa-rica finished.')
        return True
    
    def update(self):
        _logger.info('Updating Odoo development repository.')
        
        _logger.info('Cloning odoo source.')
        self._update_project('odoo')
        _logger.info('Cloning odoo source finished.')
        self._update_project('odoo-fork')
        self._update_project('odoo-clearcorp')
        self._update_project('odoo-costa-rica')
        
        return True
