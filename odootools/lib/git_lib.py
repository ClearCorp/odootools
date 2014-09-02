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
Description: Install git
'''

import logging
from odootools.lib import tools

_logger = logging.getLogger('oerptools.lib.git')

def git_install():
    os_version = tools.get_os()
    if os_version and os_version['os'] == 'Linux':
        if (os_version['version'][0] == 'Ubuntu') or (os_version['version'][0] == 'LinuxMint'):
            return ubuntu_git_install()
        elif os_version['version'][0] == 'arch':
            return arch_git_install()
    _logger.warning('Can\'t install git in this OS (%s)' % os_version['version'][0])
    return False

def ubuntu_git_install():
    _logger.info('Installing git...')
    return tools.ubuntu_install_package(['git', 'python-git'], update=True)

def arch_git_install():
    # TODO: check arch packages
    _logger.info('Installing git...')
    return tools.arch_install_repo_package(['git','python-git'])

def git_init_repo(target):
    from git import Repo
    repo = Repo.init(target)
    if repo: return True
    return False
    

def git_clone(source, target, branch=None):
    from git import Repo
    try:
        if branch:
            repo = Repo.clone_from(source, target, branch=branch)
        else:
            repo = Repo.clone_from(source, target)
    except Exception as e:
        _logger.error('Git Clone: Cloning the repo %s has failed.' % (target))
        return False
    return repo

def git_pull(source, remote=None, branch=None):
    from git import Repo
    try:
        repo = Repo(source)
        if not remote:
            remote = repo.remotes.origin
        if not branch:
            branch = repo.active_branch.name
        remote.pull(branch)
    except AssertionError as e:
        _logger.error('Git Pull: The provided source branch (%s) is up to date.' % source)
        return False
    except:
        _logger.error('Git Pull: The provided source branch (%s) can\'t be opened.' % source)
        return False
    return True

def git_push(source, remote=None, branch=None):
    from git import Repo
    try:
        repo = Repo(source)
        if not remote:
            remote = repo.remotes.origin
        if not branch:
            branch = repo.active_branch.name
        remote.push(branch)
    except AssertionError as e:
        _logger.error('Git Pull: The provided source branch (%s) is up to date.' % source)
        return False
    except:
        _logger.error('Git Push: failed. Exiting.')
    return False

def git_add_remote(repo_dir, remote_name, remote_url):
    from git import Repo
    try:
        repo = Repo(repo_dir)
        try:
            remote = repo.create_remote(remote_name, remote_url)
        except:
            _logger.error('Git Pull: The provided remote %s / %s can not be added.' % (remote_name, remote_url))
            return False
    except:
        _logger.error('Opening branch failed. Exiting.')
        return False
    return True
