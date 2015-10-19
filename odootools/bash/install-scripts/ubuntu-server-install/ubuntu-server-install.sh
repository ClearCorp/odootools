#!/bin/bash

if [[ ! -d $OPENERP_CCORP_DIR ]]; then
	echo "openerp-ccorp-scripts not installed."
	exit 1
fi

#import functions
. $OPENERP_CCORP_DIR/main-lib/checkRoot.sh
. $OPENERP_CCORP_DIR/main-lib/setSources.sh
. $OPENERP_CCORP_DIR/main-lib/regenSSHKeys.sh
. $OPENERP_CCORP_DIR/main-lib/getDist.sh

# Check user is root
checkRoot

# Sets the root password.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to set root password (Y/n)? " -n 1 REPLY
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	passwd
fi
echo ""

# Configure locales
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to select locales for installation (Y/n)? " -n 1 REPLY
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	cat > /var/lib/locales/supported.d/local << EOF
en_US ISO-8859-1
en_US.UTF-8 UTF-8
es_ES.UTF-8 UTF-8
es_CR.UTF-8 UTF-8
EOF
	REPLY="Y"
	while [[ $REPLY =~ ^[Yy]$ ]]; do
		REPLY=""
		while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
			echo "Locales ready to install:"
			cat /var/lib/locales/supported.d/local
			read -p "Do you want to select another locale for installation (Y/n)?: " -n 1 REPLY
			if [[ $REPLY == "" ]]; then
				REPLY="y"
			fi
			echo ""
		done
		if [[ $REPLY =~ ^[Yy]$ ]]; then
			def_locale=""
			read -p "Enter the extra locale to install: " def_locale
			if [[ `grep -c "$def_locale" /usr/share/i18n/SUPPORTED` == 0 ]]; then
				echo "Locale $def_locale invalid. Please enter a valid locale."
				echo "See /usr/share/i18n/SUPPORTED for a complete list of valid locales."
			elif [[ `grep -c "$def_locale" /usr/share/i18n/SUPPORTED` > 1 ]]; then
				echo "Several locales found with your entry, please be more specific:"
				grep "$def_locale" /usr/share/i18n/SUPPORTED
			elif [[ `grep -c "$def_locale" /var/lib/locales/supported.d/local` > 0 ]]; then
				echo "Locale $def_locale is already selected."
			else
				echo "Selecting $def_locale for installation"
				echo `grep "$def_locale" /usr/share/i18n/SUPPORTED` >> /var/lib/locales/supported.d/local
			fi
		fi
	done
	locale-gen
fi
echo ""

# Configure locales
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to set the default locale (Y/n)? " -n 1 REPLY
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	no_locale=1
	while [[ $no_locale == 1 ]]; do
		echo "Locales installed:"
		cat /var/lib/locales/supported.d/local
		read -p "Enter the default locale for this machine (en_US.UTF-8): " def_locale
		if [[ $def_locale == "" ]]; then
			def_locale="en_US.UTF-8"
		fi
		if [[ `egrep -c "^$def_locale " /var/lib/locales/supported.d/local` > 0 ]]; then
			no_locale=0
		else
			echo "Locale $def_locale invalid. Please enter a valid installed locale."
		fi
	done
	if [[ `grep -c LC_CTYPE /etc/environment` == 0 ]]; then
		echo "LC_CTYPE=\"$def_locale\"" >> /etc/environment
	else
		sed -i "s/LC_CTYPE=.*/LC_CTYPE=$def_locale/g" /etc/environment
	fi
	if [[ `grep -c LC_MESSAGES /etc/environment` == 0 ]]; then
		echo "LC_MESSAGES=\"$def_locale\"" >> /etc/environment
	else
		sed -i "s/LC_MESSAGES=.*/LC_MESSAGES=$def_locale/g" /etc/environment
	fi
	if [[ `grep -c LC_ALL /etc/environment` == 0 ]]; then
		echo "LC_ALL=\"$def_locale\"" >> /etc/environment
	else
		sed -i "s/LC_ALL=.*/LC_ALL=$def_locale/g" /etc/environment
	fi
fi
echo ""

# Sets the hostname.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to set the hostname (Y/n)? " -n 1 REPLY
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	while [[ $new_hostname == "" ]]; do
		read -p "Enter the hostname of this machine (not the FQDN) (`cat /etc/hostname`): " new_hostname
		if [[ $new_hostname == "" ]]; then
			new_hostname=`cat /etc/hostname`
		fi
		echo ""
	done
	while [[ $new_hostname_full == "" ]]; do
		read -p "Enter the FQDN of this machine (`hostname --fqdn`): " new_hostname_full
		if [[ $new_hostname_full == "" ]]; then
			new_hostname_full=`hostname --fqdn`
		fi
		echo ""
	done
	while [[ $ip_addr == "" ]]; do
		echo "What is your IP address (list: `ifconfig  | grep 'inet:\|inet addr:'| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1}'`): "
		read -p "WARNING: IP address not verified, WRITE IT CAREFULLY!!: " ip_addr
		echo ""
	done
	echo $new_hostname > /etc/hostname
	cat > /etc/hosts <<EOF
127.0.0.1	localhost.localdomain localhost
$ip_addr	$new_hostname_full $new_hostname
EOF
	chmod 644 /etc/hosts
	chmod 644 /etc/hostname
	echo "Hostname set to: $(hostname)"
	echo "Hostname set to: $(hostname --fqdn)"
fi
echo ""

# Sets the timezone.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to set the timezone (Y/n)? " -n 1 REPLY
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	echo "Setting timezone..."
	dpkg-reconfigure tzdata
fi
echo ""

# Sync time with NTP
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to sync the system time with NTP (Y/n)? " -n 1 REPLY
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	echo "Setting system time syncronization..."
	apt-get -y install ntp
	# Adds 4 north america servers and comment out ntp.ubuntu.com (default)
	if [[ `cat /etc/ntp.conf | grep -c "^server ntp.ubuntu.com$"` != 0 ]]; then
		newserver=""
		newserver=$newserver"#server ntp.ubuntu.com\\n"
		newserver=$newserver"server 0.north-america.pool.ntp.org\\n"
		newserver=$newserver"server 1.north-america.pool.ntp.org\\n"
		newserver=$newserver"server 2.north-america.pool.ntp.org\\n"
		newserver=$newserver"server 3.north-america.pool.ntp.org\\n"
		sed -i "s/^server .*$/$newserver/g" /etc/ntp.conf
	fi
fi
echo ""

# Sets apt sources.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to set the apt sources (If you added manual sources to the main file they will be replaced, enter "p" to print the actual file on screen) (Y/n/p)? " -n 1 REPLY
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	elif [[ $REPLY == "p" ]]; then
		cat /etc/apt/sources.list
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	dist=""
	getDist dist
	setSources_ubuntu $dist
	echo "Apt sources set."
		REPLY='none'
		while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
			read -p "Do you want to disable source repositories (Y/n)? " -n 1 REPLY
			if [[ $REPLY == "" ]]; then
				REPLY="y"
			fi
			echo ""
		done
		if [[ $REPLY =~ ^[Yy]$ ]]; then
			setSources_disable_src $dist
		fi
		REPLY='none'
		while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
			read -p "Do you want to disable restricted repositories (not full OpenSource packages) (y/N)? " -n 1 REPLY
			if [[ $REPLY == "" ]]; then
				REPLY="n"
			fi
			echo ""
		done
		if [[ $REPLY =~ ^[Yy]$ ]]; then
			setSources_disable_restricted $dist
		fi
		REPLY='none'
		while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
			read -p "Do you want to disable universe repositories (community maintained software) (y/N)? " -n 1 REPLY
			if [[ $REPLY == "" ]]; then
				REPLY="n"
			fi
			echo ""
		done
		if [[ $REPLY =~ ^[Yy]$ ]]; then
			setSources_disable_universe $dist
		fi
		REPLY='none'
		while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
			read -p "Do you want to disable multiverse repositories (closed source software) (Y/n)? " -n 1 REPLY
			if [[ $REPLY == "" ]]; then
				REPLY="y"
			fi
			echo ""
		done
		if [[ $REPLY =~ ^[Yy]$ ]]; then
			setSources_disable_multiverse $dist
		fi
		REPLY='none'
		while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
			read -p "Do you want to disable backport updates repositories (unsupported updates) (Y/n)? " -n 1 REPLY
			if [[ $REPLY == "" ]]; then
				REPLY="y"
			fi
			echo ""
		done
		if [[ $REPLY =~ ^[Yy]$ ]]; then
			setSources_disable_backports $dist
		fi
		REPLY='none'
		while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
			read -p "Do you want to disable proposed updates repositories (pre-release updates) (Y/n)? " -n 1 REPLY
			if [[ $REPLY == "" ]]; then
				REPLY="y"
			fi
			echo ""
		done
		if [[ $REPLY =~ ^[Yy]$ ]]; then
			setSources_disable_proposed $dist
		fi
fi
echo ""

# Update the system.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to update the system (Y/n)? " -n 1 REPLY
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	apt-get -y update
	apt-get -y upgrade
	echo "System up-to-date."
fi
echo ""

# Install webmin
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to install webmin (Y/n)? " -n 1 REPLY
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	setSources_webmin $dist
	apt-get -y update
	apt-get -y install webmin
	echo "Webmin is installed."
fi
echo ""

# Remove unnecesary packages and daemons.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to remove unnecesary packages and daemons (ONLY recommended for a server) (y/N)? " -n 1 REPLY
	if [[ $REPLY == "" ]]; then
		REPLY="n"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	apt-get -y --purge remove pcmciautils wpasupplicant wireless-tools exim4 exim4-base exim4-config exim4-daemon-light mailx
	apt-get -y autoremove
fi
echo ""

# Install extra packages.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to install extra packages (Y/n)? " -n 1 REPLY
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	read -p "List the packages to install (acpid dnsutils ifstat traceroute locate psmisc nmap python-software-properties aptitude synaptic iotop htop)? " packages
	if [[ $packages == "" ]]; then
		packages="acpid dnsutils ifstat traceroute locate psmisc nmap python-software-properties aptitude synaptic iotop htop"
	fi
	echo ""
	apt-get -y install $packages
fi
echo ""

# Clean apt cache.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to clean apt cache (Y/n)? " -n 1 REPLY
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	apt-get clean
fi
echo ""

# Regenerate SSH keys on next reboot.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to regenerate SSH keys on next reboot (ONLY needed to clone a virtual instance) (y/N)? " -n 1 REPLY
	if [[ $REPLY == "" ]]; then
		REPLY="n"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	regenSSHKeys
	echo "SSH keys will be regenerated on next reboot."
fi
echo ""

exit 0
