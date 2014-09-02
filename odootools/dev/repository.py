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
    
    def _update_project(self, name, ccorp, branches):
        _logger.info('Updating development repository for %s, branches: %s.' % (name, branches))
        
        project_dir = os.path.abspath(self._repo_dir) + '/%s' % name
        
        if not os.path.isdir(project_dir):
            _logger.error('Repository %s doesn\'t exists. Exiting.' % name)
            return False
        
        for branch in branches:
            _logger.info('Updating %s/%s.' % (name, branch))
            
            if not os.path.isdir('%s/main/%s' % (project_dir, branch)):
                _logger.warning('Branch %s/%s doesn\'t exists. Skipping.' % (name, branch))
            else:
                if bzr.bzr_pull('%s/main/%s' % (project_dir, branch)):
                    _logger.info('Pull OK: %s/%s.' % (name, branch))
                else:
                    _logger.error('Pull ERROR: %s/%s.' % (name, branch))
            
            if ccorp:
                if not os.path.isdir('%s/main/%s-ccorp' % (project_dir, branch)):
                    _logger.warning('Branch %s/%s-ccorp doesn\'t exists. Skipping.' % (name, branch))
                else:
                    if bzr.bzr_pull('%s/main/%s-ccorp' % (project_dir, branch)):
                        _logger.info('Pull OK: %s/%s-ccorp.' % (name, branch))
                    else:
                        _logger.error('Pull ERROR: %s/%s-ccorp.' % (name, branch))
                    
                    if bzr.bzr_pull('%s/main/%s-ccorp' % (project_dir, branch), bzr.bzr_get_push_location('%s/main/%s-ccorp' % (project_dir, branch))):
                        _logger.info('Pull :push OK: %s/%s-ccorp.' % (name, branch))
                    else:
                        _logger.error('Pull :push ERROR: %s/%s-ccorp.' % (name, branch))
                    
                    if self._push:
                        if bzr.bzr_push('%s/main/%s-ccorp' % (project_dir, branch)):
                            _logger.info('Push OK: %s/%s-ccorp.' % (name, branch))
                        else:
                            _logger.error('Push ERROR: %s/%s-ccorp.' % (name, branch))
            else:
                if self._push:
                    if bzr.bzr_push('%s/main/%s' % (project_dir, branch)):
                        _logger.info('Push OK: %s/%s.' % (name, branch))
                    else:
                        _logger.error('Push ERROR: %s/%s.' % (name, branch))
        return True
    
    def _reset_project_locations(self, name, ccorp, branches):
        _logger.info('Reseting branch locations for development repository %s, branches: %s.' % (name, branches))
        
        project_dir = os.path.abspath(self._repo_dir) + '/%s' % name
        
        if not os.path.isdir(project_dir):
            _logger.error('Repository %s doesn\'t exists. Exiting.' % name)
            return False
        
        for branch in branches:
            official_branch = 'lp:%s/%s' % (name, branch)
            ccorp_branch = 'lp:~clearcorp-drivers/%s/%s-ccorp' % (name, branch)
            _logger.info('Reseting locations for %s/%s.' % (name, branch))
            bzr.bzr_set_parent('%s/main/%s' % (project_dir, branch), official_branch)
            bzr.bzr_set_push_location('%s/main/%s' % (project_dir, branch), official_branch)
            if ccorp:
                bzr.bzr_set_parent('%s/main/%s-ccorp' % (project_dir, branch), official_branch)
                bzr.bzr_set_push_location('%s/main/%s-ccorp' % (project_dir, branch), ccorp_branch)
            
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
        bzr.bzr_initialize()
        _logger.info('Updating OpenERP development repository.')
        if not self._repo_exists:
            _logger.info('Repository doesn\'t exist in: %s. Exiting.' % self._repo_dir)
            return False
        
        self._update_project('openobject-server',     True,  ['6.1', '7.0', 'trunk'])
        self._update_project('openobject-addons',     True,  ['6.1', '7.0', 'trunk', 'extra-trunk'])
        self._update_project('openobject-client',     True,  ['6.1', 'trunk'])
        self._update_project('openerp-web',           True,  ['6.1', '7.0', 'trunk'])
        self._update_project('openobject-doc',        True,  ['6.1'])
        
        self._update_project('openerp-ccorp-addons',  False, ['6.1', '7.0', 'trunk'])
        self._update_project('openerp-costa-rica',    False, ['6.1', '7.0', 'trunk'])
        self._update_project('oerptools',             False, ['1.0', '2.0', 'trunk'])
        
        self._update_project('banking-addons',        True,  ['6.1'])
        
        return True
    
    def reset_branch_locations(self):
        bzr.bzr_initialize()
        _logger.info('Reseting OpenERP development repository branch locations.')
        if not self._repo_exists:
            _logger.info('Repository doesn\'t exist in: %s. Exiting.' % self._repo_dir)
            return False
        
        self._reset_project_locations('openobject-server',     True,  ['6.1', '7.0', 'trunk'])
        self._reset_project_locations('openobject-addons',     True,  ['6.1', '7.0', 'trunk', 'extra-trunk'])
        self._reset_project_locations('openobject-client',     True,  ['6.1', 'trunk'])
        self._reset_project_locations('openerp-web',           True,  ['6.1', '7.0', 'trunk'])
        self._reset_project_locations('openobject-doc',        True,  ['6.1'])
        
        self._reset_project_locations('openerp-ccorp-addons',  False, ['6.1', '7.0', 'trunk'])
        self._reset_project_locations('openerp-costa-rica',    False, ['6.1', '7.0', 'trunk'])
        self._reset_project_locations('oerptools',             False, ['1.0', '2.0', 'trunk'])
        
        self._reset_project_locations('banking-addons',        True,  ['6.1'])
        
        return True
    
    def _src_branch_project(self, name, ccorp, branches):
        _logger.info('Creating sources repository for %s, branches: %s.' % (name, branches))
        
        project_dir = os.path.abspath(self._repo_dir) + '/%s' % name
        src_dir = os.path.abspath(self._repo_dir) + '/openerp-src/src'
        
        for branch in branches:
            _logger.info('Creating branch for %s/%s.' % (name, branch))
            
            if ccorp:
                project_branch_dir = '%s/main/%s-ccorp' % (project_dir, branch)
            else:
                project_branch_dir = '%s/main/%s' % (project_dir, branch)
            
            src_branch_dir = '%s/%s/%s' % (src_dir, branch, name)
            repo_branch_dir = '%s/openerp/%s/%s' % (src_dir, branch, name)
            
            if not os.path.isdir('%s/openerp' % src_dir):
                _logger.info('Creating OpenERP sources main repository.')
                bzr.bzr_init_repo('%s/openerp' % src_dir, no_trees=True)
            
            _logger.info('Source branch: %s.' % project_branch_dir)
            if os.path.isdir(src_branch_dir):
                _logger.warning('Branch at %s alredy exists. Delete it before running the script to recreate.' % src_branch_dir)
            else:
                if not os.path.isdir('%s/%s' % (src_dir, branch)):
                    os.makedirs('%s/%s' % (src_dir, branch))
                bzr.bzr_branch(project_branch_dir, src_branch_dir, no_tree=True)
            bzr.bzr_set_parent(src_branch_dir, project_branch_dir)
            if os.path.isdir(repo_branch_dir):
                _logger.warning('Branch at %s alredy exists. Delete it before running the script to recreate.' % repo_branch_dir)
            else:
                if not os.path.isdir('%s/openerp/%s' % (src_dir, branch)):
                    os.makedirs('%s/openerp/%s' % (src_dir, branch))
                bzr.bzr_branch(project_branch_dir, repo_branch_dir, no_tree=True)
            bzr.bzr_set_parent(repo_branch_dir, project_branch_dir)
        return True
    
    def _src_update_project(self, name, ccorp, branches):
        _logger.info('Updating sources repository for %s, branches: %s.' % (name, branches))
        
        src_dir = os.path.abspath(self._repo_dir) + '/openerp-src/src'
        
        for branch in branches:
            _logger.info('Updating branch for %s/%s.' % (name, branch))
            
            src_branch_dir = '%s/%s/%s' % (src_dir, branch, name)
            repo_branch_dir = '%s/openerp/%s/%s' % (src_dir, branch, name)
            _logger.info('Source branch: %s.' % src_branch_dir)
            
            if not os.path.isdir(src_branch_dir):
                _logger.error('Branch at %s doesn\'t exist. Skipping.' % src_branch_dir)
            else:
                bzr.bzr_pull(src_branch_dir)
            if not os.path.isdir(repo_branch_dir):
                _logger.error('Branch at %s doesn\'t exist. Skipping.' % repo_branch_dir)
            else:
                bzr.bzr_pull(repo_branch_dir)
        return True
    
    def _src_compress_project(self, name, ccorp, branches):
        import tarfile
        _logger.info('Compressing sources repository for %s, branches: %s.' % (name, branches))
        
        src_dir = os.path.abspath(self._repo_dir) + '/openerp-src/src'
        bin_dir = os.path.abspath(self._repo_dir) + '/openerp-src/bin'
        
        for branch in branches:
            _logger.info('Compressing branch for %s/%s.' % (name, branch))
            
            src_branch_dir = '%s/%s/%s' % (src_dir, branch, name)
            repo_branch_dir = '%s/openerp/%s/%s' % (src_dir, branch, name)
            _logger.info('Source branch: %s.' % src_branch_dir)
            
            if not os.path.isdir(src_branch_dir):
                _logger.error('Branch at %s doesn\'t exist. Skipping.' % src_branch_dir)
            else:
                if not os.path.isdir('%s/%s' % (bin_dir, branch)):
                    os.makedirs('%s/%s' % (bin_dir, branch))
                tar = tarfile.open('%s/%s/%s.tgz' % (bin_dir, branch, name), "w:gz")
                tar.add(src_branch_dir, arcname='%s/%s' % (branch, name))
                tar.close()
        return True
    
    def _src_compress_repo(self):
        import tarfile
        _logger.info('Compressing main sources repository.')
        
        src_dir = os.path.abspath(self._repo_dir) + '/openerp-src/src'
        bin_dir = os.path.abspath(self._repo_dir) + '/openerp-src/bin'
        
        if not os.path.isdir('%s/openerp' % src_dir):
            _logger.error('Repository at %s doesn\'t exist. Exiting.' % src_dir)
            return False
        if not os.path.isdir(bin_dir):
            os.makedirs(bin_dir)
        tar = tarfile.open('%s/openerp.tgz' % bin_dir, "w:gz")
        tar.add('%s/openerp/.bzr' % src_dir, arcname='openerp/.bzr')
        tar.close()
        return True
    
    def src_make(self):
        bzr.bzr_initialize()
        _logger.info('Making new OpenERP sources repository.')
        if not self._repo_exists:
            _logger.info('Repository doesn\'t exist in: %s. Exiting.' % self._repo_dir)
            return False
        
        self._src_branch_project('openobject-server',     True,  ['6.1', '7.0', 'trunk'])
        self._src_branch_project('openobject-addons',     True,  ['6.1', '7.0', 'trunk'])
        self._src_branch_project('openerp-web',           True,  ['6.1', '7.0', 'trunk'])
        
        self._src_branch_project('openerp-ccorp-addons',  False, ['6.1', '7.0', 'trunk'])
        self._src_branch_project('openerp-costa-rica',    False, ['6.1', '7.0', 'trunk'])
        
        self._src_branch_project('banking-addons',        True,  ['6.1'])
        
        self._src_compress_project('openobject-server',     True,  ['6.1', '7.0', 'trunk'])
        self._src_compress_project('openobject-addons',     True,  ['6.1', '7.0', 'trunk'])
        self._src_compress_project('openerp-web',           True,  ['6.1', '7.0', 'trunk'])
        
        self._src_compress_project('openerp-ccorp-addons',  False, ['6.1', '7.0', 'trunk'])
        self._src_compress_project('openerp-costa-rica',    False, ['6.1', '7.0', 'trunk'])
        
        self._src_compress_project('banking-addons',        True,  ['6.1'])
        
        self._src_compress_repo()
        
        return True
    
    def src_update(self):
        bzr.bzr_initialize()
        _logger.info('Updating OpenERP sources repository.')
        if not self._repo_exists:
            _logger.info('Repository doesn\'t exist in: %s. Exiting.' % self._repo_dir)
            return False
        
        self._src_update_project('openobject-server',     True,  ['6.1', '7.0', 'trunk'])
        self._src_update_project('openobject-addons',     True,  ['6.1', '7.0', 'trunk'])
        self._src_update_project('openerp-web',           True,  ['6.1', '7.0', 'trunk'])
        
        self._src_update_project('openerp-ccorp-addons',  False, ['6.1', '7.0', 'trunk'])
        self._src_update_project('openerp-costa-rica',    False, ['6.1', '7.0', 'trunk'])
        
        self._src_update_project('banking-addons',        True,  ['6.1'])
        
        self._src_compress_project('openobject-server',     True,  ['6.1', '7.0', 'trunk'])
        self._src_compress_project('openobject-addons',     True,  ['6.1', '7.0', 'trunk'])
        self._src_compress_project('openerp-web',           True,  ['6.1', '7.0', 'trunk'])
        
        self._src_compress_project('openerp-ccorp-addons',  False, ['6.1', '7.0', 'trunk'])
        self._src_compress_project('openerp-costa-rica',    False, ['6.1', '7.0', 'trunk'])
        
        self._src_compress_project('banking-addons',        True,  ['6.1'])
        
        self._src_compress_repo()
        
        return True
