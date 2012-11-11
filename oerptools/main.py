#!/usr/bin/python2

# Add the module oerptools to PYTHONPATH
# This is necesary in order to call the module without installing it
import sys, os
sys.path.append(os.path.abspath('.'))

from oerptools.lib import webmin

webmin.webmin_install()
