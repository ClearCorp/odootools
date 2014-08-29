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

'''
Description: Install bzr
'''

import logging
from odootools.lib import tools

_logger = logging.getLogger('oerptools.lib.bzr')

def bzr_install():
    os_version = tools.get_os()
    if os_version and os_version['os'] == 'Linux':
        if (os_version['version'][0] == 'Ubuntu') or (os_version['version'][0] == 'LinuxMint'):
            return ubuntu_bzr_install()
        elif os_version['version'][0] == 'arch':
            return arch_bzr_install()
    _logger.warning('Can\'t install bzr in this OS (%s)' % os_version['version'][0])
    return False

def ubuntu_bzr_install():
    #TODO: logger gets the output of the command
    _logger.info('Installing bzr...')
    return tools.ubuntu_install_package(['bzr', 'python-bzrlib'], update=True)

def arch_bzr_install():
    #TODO: logger gets the output of the command
    _logger.info('Installing bzr...')
    return tools.arch_install_repo_package(['bzr'])

def bzr_initialize():
    _logger.debug('Importing and initializing bzrlib')
    from bzrlib.branch import Branch
    from bzrlib.trace import set_verbosity_level
    from bzrlib.plugin import load_plugins
    from bzrlib import initialize
    library_state = initialize()
    library_state.__enter__()
    set_verbosity_level(1000)
    
    import odootools.lib.logger
    odootools.lib.logger.set_levels()
    
    load_plugins()

def bzr_init_repo(target, no_trees=False):
    #TODO: do this with the python library
    if no_trees:
        if tools.exec_command('bzr init-repo --no-tree %s' % target):
            _logger.error('Failed to create repository in: %s. Exiting.' % target)
            return False
    else:
        if tools.exec_command('bzr init-repo %s' % target):
            _logger.error('Failed to create repository in: %s. Exiting.' % target)
            return False
    return True
    

def bzr_branch(source, target, no_tree=None):
    from bzrlib.branch import Branch
    from bzrlib.transport import get_transport
    
    try:
        source_branch = Branch.open(source)
    except:
        _logger.error('Bzr branch: The provided source branch (%s) can\'t be opened.' % source)
        return False
    
    if no_tree:
        tree = False
    else:
        tree = True
    
    branch = source_branch.bzrdir.sprout(target, create_tree_if_local=tree).open_branch()
    try:
        pass
    except Exception as e:
        _logger.error('Bzr branch: The branch to %s failed.' % (target))
        return False
    
    return branch

def bzr_pull(target, source=None):
    from bzrlib.branch import Branch
    from bzrlib.workingtree import WorkingTree
    try:
        branch = Branch.open(target)
    except:
        _logger.error('Bzr pull: The provided target branch (%s) can\'t be opened.' % target)
        return False
    try:
        tree = WorkingTree.open(target)
    except:
        tree = False
    
    if source:
        try:
            branch.pull(Branch.open(source))
            if tree:
                tree.update()
        except:
            _logger.error('Bzr pull: The provided source branch (%s) can\'t be opened.' % source)
            return False
    else:
        try:
            branch.pull(Branch.open(branch.get_parent()))
            if tree:
                tree.update()
        except:
            _logger.error('Bzr pull: The provided source branch (%s) can\'t be opened.' % branch.get_parent())
            return False
    
    return True

def bzr_push(source, target=None):
    from bzrlib.branch import Branch
    try:
        branch = Branch.open(source)
    except:
        _logger.error('Bzr push: The provided source branch (%s) can\'t be opened.' % source)
        return False
    
    if target:
        try:
            target = Branch.open(target)
        except:
            _logger.error('Bzr push: The provided target branch (%s) can\'t be opened.' % target)
            return False
        try:
            return branch.push(target)
        except:
            _logger.error('Bzr push: failed. Exiting.')
    else:
        try:
            return branch.push()
        except:
            _logger.error('Bzr push: failed. Exiting.')
    return False

def bzr_set_parent(branch, parent):
    from bzrlib.branch import Branch
    try:
        branch = Branch.open(branch)
    except:
        _logger.error('Bzr set_parent: The provided target branch (%s) can\'t be opened.' % branch)
        return False
    return branch.set_parent(parent)

def bzr_set_push_location(branch, location):
    from bzrlib.branch import Branch
    try:
        branch = Branch.open(branch)
    except:
        _logger.error('Bzr set_push_location: The provided target branch (%s) can\'t be opened.' % branch)
        return False
    return branch.set_push_location(location)

def bzr_get_push_location(branch):
    from bzrlib.branch import Branch
    try:
        branch = Branch.open(branch)
    except:
        _logger.error('Bzr get_push_location: The provided target branch (%s) can\'t be opened.' % branch)
        return False
    return branch.get_push_location()
