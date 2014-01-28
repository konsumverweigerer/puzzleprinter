import os
import sys

path = '/data/puzzleprinter'
if path not in sys.path:
    sys.path.append(path)
os.chdir(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


