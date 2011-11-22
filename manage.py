#!/usr/bin/env python
# we need to include third party modules path here
# note this is only for development,
# proper path to libs have to be inserted by wsgi configuration for development
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'libs'))

#rest of standard manage.py file
from django.core.management import execute_manager
import imp

try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

import settings

if __name__ == "__main__":
    execute_manager(settings)
