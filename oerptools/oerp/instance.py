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
_logger = logging.getLogger('oerptools.oerp.instance')

import os, re

from oerptools.lib import config, bzr, tools

class oerpInstance(object):
    def __init__(self):
        self._os_info = tools.get_os()
        #Old Ubuntu versions have a suffix in postgresql init script
        self._postgresql_init_suffix = ''
        self._postgresql_version = ''
        if self._os_info['os'] == 'Linux' and self._os_info['version'][0] == 'Ubuntu':
            if self._os_info['version'][1] in ('10.04','10.10'):
                self._postgresql_init_suffix = '-8.4'
            if self._os_info['version'][1] < '11.10':
                self._postgresql_version = '8.4'
            else:
                self._postgresql_version = '9.1'
        
        self._branch = config.params['branch'] or '7.0'
        self._name = config.params['name']
        self._installation_type = config.params[branch+'_'+self._name+'_installation_type'] or \
                                  config.params[branch+'_installation_type'] or \
                                  config.params['installation_type'] or 'dev'
        self._user = config.params[branch+'_'+self._name+'_user'] or \
                     config.params[branch+'_user'] or \
                     config.params['user'] or None
        self._port = config.params[branch+'_'+self._name+'_port'] or \
                     config.params[branch+'_port'] or \
                     config.params['port'] or 0
        self._install_openobject_addons = config.params[branch+'_'+self._name+'_install_openobject_addons'] or \
                                          config.params[branch+'_install_openobject_addons'] or \
                                          config.params['install_openobject_addons'] or True
        self._install_openerp_ccorp_addons = config.params[branch+'_'+self._name+'_install_openerp_ccorp_addons'] or \
                                             config.params[branch+'_install_openerp_ccorp_addons'] or \
                                             config.params['install_openerp_ccorp_addons'] or True
        self._install_openerp_costa_rica = config.params[branch+'_'+self._name+'_install_openerp_costa_rica'] or \
                                           config.params[branch+'_install_openerp_costa_rica'] or \
                                           config.params['install_openerp_costa_rica'] or True
        self._admin_password = config.params[branch+'_'+self._name+'_admin_password'] or \
                               config.params[branch+'_admin_password'] or \
                               config.params['admin_password'] or None
        self._postgresql_password = config.params[branch+'_'+self._name+'_postgresql_password'] or \
                                    config.params[branch+'_postgresql_password'] or \
                                    config.params['postgresql_password'] or None
        self._start_now = config.params[branch+'_'+self._name+'_start_now'] or \
                          config.params[branch+'_start_now'] or \
                          config.params['start_now'] or (self._installation_type == 'server' and True) or False
        self._on_boot = config.params[branch+'_'+self._name+'_on_boot'] or \
                        config.params[branch+'_on_boot'] or \
                        config.params['on_boot'] or (self._installation_type == 'server' and True) or False
        return super(oerpInstance, self).__init__()
    
    def _check_port(self, port):
        for key, value in config.params:
            match = re.match(r'^([0-9]{1}\.[0-9]{1})_([0-9a-z_]+)_port$|^(trunk)_([0-9a-z_]+)_port$', key)
            if match:
                if value == port:
                    return match.group(1,2)
        return False
    
    def _add_postgresql_user(self):
        _logger.info('Adding PostgreSQL user: openerp_%s.' % self._name)
        if tools.exec_command('adduser --system --home /var/run/openerp/%s --no-create-home --ingroup openerp openerp_%s' % (self._name, self._name)):
            _logger.error('Failed to add system user. Exiting.')
            return False
        if tools.exec_command('sudo -u postgres createuser openerp_%s --superuser --createdb --no-createrole' % self._name):
            _logger.error('Failed to add PostgreSQL user. Exiting.')
            return False
        if tools.exec_command('sudo -u postgres psql template1 -U postgres -c "alter user \\"openerp_%s\\" with password \'%s\'"' % (self._name, self._admin_password)):
            _logger.error('Failed to set PostgreSQL user password. Exiting.')
            return False
        return True

    def install(self):
        _logger.info('OpenERP instance installation started.')
        
        _logger.info('')
        _logger.info('Please check the following information before continuing.')
        _logger.info('=========================================================')
        
        if not self._user:
            if self._installation_type == 'dev':
                self._user = pwd.getpwuid(os.getuid()).pw_name
            elif self._installation_type == 'server':
                self._user = 'openerp'
        if pwd.getpwuid(os.getuid()).pw_name not in (self._user, 'root'):
            try:
                group = grp.getgrnam('openerp')
                if not pwd.getpwuid(os.getuid()).pw_name in group['gr_mem']:
                    _logger.error('Your user must be the user of installation (%s), root, or be part of openerp group. Exiting.')
                    return False
            except:
                _logger.error('Your user must be the user of installation (%s), root, or be part of openerp group. Exiting.')
                return False
        
        installed_branches = []
        if os.path.isdir('/etc/openerp/6.1'):
            installed_branches.append('6.1')
        if os.path.isdir('/etc/openerp/7.0'):
            installed_branches.append('7.0')
        if os.path.isdir('/etc/openerp/trunk'):
            installed_branches.append('trunk')
        
        if not installed_branches:
            _logger.error('No OpenERP server versions installed. Exiting.')
            return False
        elif len(installed_branch) == 1:
            if self._branch not in installed_branches:
                _logger.warning('Selected branch (%s) not installed. Using %s instead.' % (self._branch, installed_branch[0]))
                self._branch = installed_branch[0]
        else:
            if self._branch not in installed_branches:
                _logger.error('Selected branch (%s) not installed. Exiting.' % self._branch)
                return False
        
        _logger.info('OpenERP version (branch) used by this instance: %s' % self._branch)
        
        if re.match(r'[0-9a-z_]+', self._name):
            _logger.info('Instance name: %s' % self._name)
        else:
            _logger.error('Selected name (%s) has invalid characters. Use only lowercase letters, digits and underscore. Exiting.' % self._name)
            return False
        
        if not self._port:
            _logger.error('Instance port unknown. Exiting.')
            return False
        elif self._port >= 0 and self._port <= 99:
            check_port = self._check_port(self._port)
            if check_port:
                _logger.error('Selected port (%s) is in use by instance %s (%s). Exiting.' % (self._port, check_port[1], check_port[0]))
                return False
            else:
                _logger.info('Instance port number: %s' % self._port)
        else:
            _logger.error('Selected port (%s) is invalid. Port number must be an integer number between 0 and 99. Exiting.' % self._port)
            return False
        
        if self._start_now:
            _logger.info('Instance will be started at the end of this installation.')
        else:
            _logger.info('Instance will NOT be started at the end of this installation.')
        
        if self._on_boot:
            _logger.info('Instance will be started on boot.')
        else:
            _logger.info('Instance will NOT be started on boot.')
        
        _logger.info('')
        _logger.info('Please review the values above and confirm accordingly.')
        answer = False
        while not answer:
            answer = raw_input('Are the configuration values correct (y/n)? ')
            if re.match(r'^y$|^yes$', answer, flags=re.IGNORECASE):
                answer = 'y'
            elif re.match(r'^n$|^no$', answer, flags=re.IGNORECASE):
                answer = 'n'
                _logger.error('The configuration values are incorrect. Please correct any configuration error and run the script again.')
                return False
            else:
                answer = False
        
        #Update config file with new values
        values = {
            'oerp-instance-make': {
                self._branch+'_'+self._name+'_installation_type': self._installation_type,
                self._branch+'_'+self._name+'_user': self._user,
                self._branch+'_'+self._name+'_port': self._port,
                self._branch+'_'+self._name+'_install_openobject_addons': self._install_openobject_addons,
                self._branch+'_'+self._name+'_install_openerp_ccorp_addons': self._install_openerp_ccorp_addons,
                self._branch+'_'+self._name+'_install_openerp_costa_rica': self._install_openerp_costa_rica,
                self._branch+'_'+self._name+'_admin_password': self._admin_password,
                self._branch+'_'+self._name+'_postgresql_password': self._postgresql_password,
                self._branch+'_'+self._name+'_start_now': self._start_now,
                self._branch+'_'+self._name+'_on_boot': self._on_boot,
            },
        }
        
        config_file_path = config.params.update_config_file_values(values)
        if config_file_path:
            _logger.info('Updated config file with installation values: %s' % config_file_path)
        else:
            _logger.warning('Failed to update config file with installation values.')
        
        _logger.info('')
        _logger.info('Installing OpenERP instance')
        _logger.info('===========================')
        _logger.info('')
        
        self._add_postgresql_user()
        
        os.makedirs('/srv/openerp/%s/instances/%s/addons' % (self._branch, self._name))
        os.makedirs('/srv/openerp/%s/instances/%s/filestore' % (self._branch, self._name))
        os.symlink('/srv/openerp/%s/src/openobject-server' % self._branch, '/srv/openerp/%s/instances/%s/server' % (self._branch, self._name))
        
        installed_addons=[]
        os.symlink('/srv/openerp/%s/src/openerp-web' % self._branch, '/srv/openerp/%s/instances/%s/addons/openerp-web' % (self._branch, self._name))
        for path in os.listdir('/srv/openerp/%s/src' % self._branch):
            if path not in ('openobject-server', 'openobject-client', 'openobject-client-web', 'openerp-web'):
                os.symlink('/srv/openerp/%s/src/%s' % (self._branch, path), '/srv/openerp/%s/instances/%s/addons/%s' % (self._branch, self._name, path))
                installed_addons.append('/srv/openerp/%s/instances/%s/addons/%s' % (self._branch, self._name, path))
        installed_addons = ','.join(installed_addons)
        
        # TODO: archlinux init
        if not tools.exec_command('cp -a /etc/openerp/%s/server/init-skeleton /etc/init.d/openerp-server-%s' % (self._branch, self._name), as_root=True):
            _logger.warning('Failed to copy init script.')
        else:
            tools.exec_command('sed -i "s#@NAME@#%s#g" /etc/init.d/openerp-server-%s' % (self._name, self._name), as_root=True)
            tools.exec_command('sed -i "s#@USER@#openerp_%s#g" /etc/init.d/openerp-server-%s' % (self._user, self._name), as_root=True)
            if self._on_boot:
                toos.exec_command('update-rc.d openerp-server-%s defaults' % self._name, as_root=True)
        
        if not tools.exec_command('cp -a /etc/openerp/%s/server/bin-skeleton /usr/local/bin/openerp-server-%s' % (self._branch, self._name), as_root=True):
            _logger.warning('Failed to copy bin script.')
        else:
            tools.exec_command('sed -i "s#@NAME@#%s#g" /usr/local/bin/openerp-server-%s' % (self._name, self._name), as_root=True)
        
        if not tools.exec_command('cp -a /etc/openerp/%s/server/conf-skeleton /etc/openerp/%s/server/%s.conf' % (self._branch, self._branch, self._name), as_root=True):
            _logger.warning('Failed to copy conf file.')
        else:
            tools.exec_command('sed -i "s#@NAME@#%s#g" /etc/openerp/%s/server/%s.conf' % (self._name, self._branch, self._name), as_root=True)
            tools.exec_command('sed -i "s#@PORT@#%s#g" /etc/openerp/%s/server/%s.conf' % (self._port, self._branch, self._name), as_root=True)
            tools.exec_command('sed -i "s#@DB_USER@#openerp_%s#g" /etc/openerp/%s/server/%s.conf' % (self._name, self._branch, self._name), as_root=True)
            tools.exec_command('sed -i "s#@XMLPORT@#20%02d#g" /etc/openerp/%s/server/%s.conf' % (self._port, self._branch, self._name), as_root=True)
            tools.exec_command('sed -i "s#@NETPORT@#21%02d#g" /etc/openerp/%s/server/%s.conf' % (self._port, self._branch, self._name), as_root=True)
            tools.exec_command('sed -i "s#@XMLSPORT@#22%02d#g" /etc/openerp/%s/server/%s.conf' % (self._port, self._branch, self._name), as_root=True)
            tools.exec_command('sed -i "s#@PYROPORT@#24%02d#g" /etc/openerp/%s/server/%s.conf' % (self._port, self._branch, self._name), as_root=True)
            tools.exec_command('sed -i "s#@ADMIN_PASSWD@#%s#g" /etc/openerp/%s/server/%s.conf' % (self._admin_password, self._branch, self._name), as_root=True)
            tools.exec_command('sed -i "s#@ADDONS@#%s#g" /etc/openerp/%s/server/%s.conf' % (installed_addons, self._branch, self._name), as_root=True)
            

log_echo "Creating openerp-server log files..."
mkdir -p /var/log/openerp/$name >> $INSTALL_LOG_FILE
touch /var/log/openerp/$name/server.log >> $INSTALL_LOG_FILE

log_echo "Creating openerp-web bin script..."
cp -a /etc/openerp/$branch/web-client/bin-skeleton /usr/local/bin/openerp-web-$name >> $INSTALL_LOG_FILE
sed -i "s#\\[NAME\\]#$name#g" /usr/local/bin/openerp-web-$name >> $INSTALL_LOG_FILE

# For OpenERP 6.1+ the web server is embedded, so no need to initiate or configure the process
if [[ "$branch" =~ ^5\.0|6\.0$ ]]; then
    log_echo "Creating openerp-web init script..."
    cp -a /etc/openerp/$branch/web-client/init-skeleton /etc/init.d/openerp-web-$name >> $INSTALL_LOG_FILE
    sed -i "s#\\[NAME\\]#$name#g" /etc/init.d/openerp-web-$name >> $INSTALL_LOG_FILE
    sed -i "s#\\[USER\\]#openerp_$name#g" /etc/init.d/openerp-web-$name >> $INSTALL_LOG_FILE
    #~ Start web client on boot
    if [[ $start_boot =~ ^[Yy]$ ]]; then
        log_echo "Creating web-client rc rules..."
        update-rc.d openerp-web-$name defaults >> $INSTALL_LOG_FILE
        log_echo ""
    fi

    log_echo "Creating openerp-web configuration file..."
    cp -a /etc/openerp/$branch/web-client/web-client.conf-$branch-skeleton /etc/openerp/$branch/web-client/$name.conf
    sed -i "s#\\[NAME\\]#$name#g" /etc/openerp/$branch/web-client/$name.conf
    sed -i "s#\\[PORT\\]#23$port#g" /etc/openerp/$branch/web-client/$name.conf
    sed -i "s#\\[SERVER_PORT\\]#21$port#g" /etc/openerp/$branch/web-client/$name.conf
    if [[ $server_type == "production" ]]; then
        sed -i "s/#\?[[:space:]]*\(dbbutton\.visible.*\)/dbbutton.visible = False/g" /etc/openerp/$branch/web-client/$name.conf
    else
        sed -i "s/#\?[[:space:]]*\(dbbutton\.visible.*\)/dbbutton.visible = True/g" /etc/openerp/$branch/web-client/$name.conf
    fi

    log_echo "Creating openerp-web log files..."
    touch /var/log/openerp/$name/web-client-access.log
    touch /var/log/openerp/$name/web-client-error.log
fi

#Change log permissions
chown -R openerp_$name:openerp /var/log/openerp/$name
chmod 664 /var/log/openerp/$name/*.log

log_echo "Creating apache rewrite file..."
cp -a /etc/openerp/apache2/ssl-$branch-skeleton /etc/openerp/apache2/rewrites/$name
sed -i "s#\\[NAME\\]#$name#g" /etc/openerp/apache2/rewrites/$name

if [[ "$branch" =~ ^6\.1|trunk$ ]]; then
    #Use OpenERP embedded XML-RPC Werzeug server
    sed -i "s#\\[PORT\\]#20$port#g" /etc/openerp/apache2/rewrites/$name >> $INSTALL_LOG_FILE
else
    #Use OpenERP Web client
    sed -i "s#\\[PORT\\]#23$port#g" /etc/openerp/apache2/rewrites/$name >> $INSTALL_LOG_FILE
fi

service apache2 reload >> $INSTALL_LOG_FILE

log_echo "Creating pid dir..."
mkdir -p /var/run/openerp/$name

#~ Start server now
if [[ $start_now =~ ^[Yy]$ ]]; then
    log_echo "Starting openerp server and web client..."
    service postgresql$postgresql_init start
    service apache2 restart
    service openerp-server-$name start
    #Start OpenERP Web client if not embedded
    if [[ "$branch" =~ ^5\.0|6\.0$ ]]; then service openerp-web-$name start; fi
    log_echo ""
fi

#~ Make developer menus
#if [[ $server_type == "station" ]]; then
#    sudo -E -u $openerp_user ccorp-openerp-mkmenus $branch $name
#fi

#~ Add server to hosts file if station

if [[ $server_type == "station" ]]; then
    echo "127.0.1.1    $name.localhost" >> /etc/hosts
fi

install_change_perms

exit 0
