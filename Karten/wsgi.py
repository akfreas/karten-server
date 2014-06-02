import os
import sys
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
sys.path.append(PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'Karten.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
