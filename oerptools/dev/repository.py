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

import logging
_logger = logging.getLogger('oerptools.dev.repository')

import os

from oerptools.lib import config, bzr, tools

class repository(object):
    def __init__(self):
        _logger.info('Initializing OpenERP development repository.')
        _repo_dir = config.params['repo_dir'] or '~/Development/openerp'
        _no_trees = config.params['no_trees'] or False
        _repo_exists = False
        
        if os.path.isdir(_repo_dir):
            _logger.info('Repository exists in: %s.' % _repo_dir)
            _logger.info('Using existing repo.')
            _repo_exists = True
        else:
            _logger.info('New repository in: %s.' % _repo_dir)
        return super(__init__, self)
    
    def _branch_project(self, name, ccorp, branches):
        _logger.info('Creating development repository for %s.' % name)
        
        project_dir = os.path.abspath(_repo_dir) + '/%s' % name
        
        if os.path.isdir(project_dir):
            _logger.info('Repository in %s already exists, delete before running the script to recreate.' % name)
        else:
            if not bzr.bzr_init_repo(project_dir, _no_trees):
                _logger.info('Failed to create repo in %s. Exiting.' % name)
                return False
        
        if not os.path.isdir('%s/main' % project_dir):
            os.mkdir('%s/main' % project_dir)
        if not os.path.isdir('%s/features' % project_dir):
            os.mkdir('%s/features' % project_dir)
        
        for branch in branches:
            official_branch = 'bzr+ssh://bazaar.launchpad.net/%2Bbranch/%s/%s' % (name, branch)
            ccorp_branch = 'bzr+ssh://bazaar.launchpad.net/%2Bbranch/~clearcorp-drivers/%s/%s-ccorp' % (name, branch)
            _logger.info('Creating branches for %s.' % branch)
            
            _logger.info('Branch: %s.' % official_branch)
            
            if os.path.isdir('%s/main/%s/.bzr' % (project_dir, branch)):
                _logger.info('%s/main/%s already exists, delete before running the script to recreate.' % (project_dir, branch))
            else:
                bzr.bzr_branch(official_branch, '%s/main/%s' % (project_dir, branch))
            
            if ccorp:
                _logger.info('Branch: %s.' % ccorp_branch)
                
                if os.path.isdir('%s/main/%s-ccorp/.bzr' % (project_dir, branch)):
                    _logger.info('%s/main/%s-ccorp already exists, delete before running the script to recreate.' % (project_dir, branch))
                else:
                    bzr.bzr_branch(ccorp_branch, '%s/main/%s-ccorp' % (project_dir, branch))
            
            _logger.info('Updating parent locations for %s.' % name)
            bzr.bzr_set_parent('%s/main/%s' % (project_dir, branch), official_branch)
            bzr.bzr_set_push_location('%s/main/%s' % (project_dir, branch), official_branch)
            if ccorp:
                bzr.bzr_set_parent('%s/main/%s-ccorp' % (project_dir, branch), official_branch)
                bzr.bzr_set_push_location('%s/main/%s-ccorp' % (project_dir, branch), ccorp_branch)
            
        return True
    
    def make(self):
        _logger.info('Making new OpenERP development repository.')
        if _repo_exists:
            _logger.info('Repository exists in: %s. Exiting.' % _repo_dir)
            return False
        
        self._branch_project(openobject-server,     True,  ['5.0', '6.0', '6.1', '7.0', 'trunk']
        self._branch_project(openobject-addons,     True,  ['5.0', '6.0', '6.1', '7.0', 'trunk', 'extra-5.0', 'extra-6.0', 'extra-trunk']
        self._branch_project(openobject-client,     True,  ['5.0', '6.0', '6.1', 'trunk']
        self._branch_project(openobject-client-web, True,  ['5.0', '6.0', 'trunk']
        self._branch_project(openerp-web,           True,  ['6.1', '7.0', 'trunk']
        self._branch_project(openobject-doc,        True,  ['5.0', '6.0', '6.1']
        
        self._branch_project(openerp-ccorp-addons,  False, ['5.0', '6.0', '6.1', '7.0', 'trunk']
        self._branch_project(openerp-costa-rica,    False, ['5.0', '6.0', '6.1', '7.0', 'trunk']
        self._branch_project(oerptools,             False, ['stable', '1.0', '2.0', 'trunk']
        
        self._branch_project(banking-addons,        True,  ['5.0', '6.0', '6.1', '7.0', 'trunk']
        
        return True
