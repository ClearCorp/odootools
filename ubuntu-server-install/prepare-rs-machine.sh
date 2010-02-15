#!/bin/bash

#import functions
. ../main/checkRoot.sh
. ../main/setSources.sh
. ../main/regenSSHKeys.sh
. ../main/getDist.sh

# Check user is root
checkRoot

# Sets the root password.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to set root password (Y/n)? " -n 1
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	passwd
fi
echo ""

# Sets the hostname.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to set the hostname (Y/n)? " -n 1
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	while [[ $new_hostname == "" ]]; do
		read -p "Enter the FQDN of this machine (`cat /etc/hostname`): " new_hostname
		if [[ $new_hostname == "" ]]; then
			new_hostname=`cat /etc/hostname`
		fi
		echo ""
	done
	sed -i "s/`cat /etc/hostname`/$new_hostname/g" /etc/hosts
	sed -i "s/`cat /etc/hostname`/$new_hostname/g" /etc/hostname
	echo "Hostname set to: $new_hostname"
fi
echo ""

# Configure locales
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to set the default locale (Y/n)? " -n 1
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	no_locale=1
	while [[ $no_locale == 1 ]]; do
		read -p "Enter the default locale for this machine (es_CR.UTF-8): " def_locale
		if [[ $def_locale == "" ]]; then
			def_locale="es_CR.UTF-8"
		fi
		if [[ `egrep -c "^$def_locale " /usr/share/i18n/SUPPORTED` > 0 ]]; then
			no_locale=0
		else
			echo "Locale $def_locale invalid. Please enter a valid locale."
			echo "See /usr/share/i18n/SUPPORTED for a complete list of valid locales."
		fi
	done
	locale-gen $def_locale
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

# Sets the local time.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to set the localtime (Y/n)? " -n 1
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	echo "Setting localtime..."
	dpkg-reconfigure tzdata
fi
echo ""

# Sets apt sources.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to set the apt sources (Y/n)? " -n 1
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	dist=""
	getDist dist
	setSources $dist
	echo "Apt sources set."
fi
echo ""

# Update the system.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to update the system (Y/n)? " -n 1
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
	read -p "Do you want to install webmin (Y/n)? " -n 1
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	apt-get -y install webmin
	echo "Webmin is installed."
fi
echo ""

# Remove unnecesary packages and daemons.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to remove unnecesary packages and daemons (Y/n)? " -n 1
	if [[ $REPLY == "" ]]; then
		REPLY="y"
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
	read -p "Do you want to install extra packages (Y/n)? " -n 1
	if [[ $REPLY == "" ]]; then
		REPLY="y"
	fi
	echo ""
done

if [[ $REPLY =~ ^[Yy]$ ]]; then
	read -p "List the packages to install (dnsutils ifstat traceroute)? " packages
	if [[ $packages == "" ]]; then
		packages="dnsutils ifstat traceroute"
	fi
	echo ""
	apt-get -y install $packages
fi
echo ""

# Clean apt cache.
REPLY='none'
while [[ ! $REPLY =~ ^[YyNn]$ ]]; do
	read -p "Do you want to clean apt cache (Y/n)? " -n 1
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
	read -p "Do you want to regenerate SSH keys on next reboot (y/N)? " -n 1
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
