import os
import sys

sys.path.append('/var/www/ec2-54-200-196-237.us-west-2.compute.amazonaws.com/tutorial')
sys.path.append('/var/www/ec2-54-200-196-237.us-west-2.compute.amazonaws.com/')

os.environ['PYTHON_EGG_CACHE'] = '/var/www/ec2-54-200-196-237.us-west-2.compute.amazonaws.com/.python-egg'

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
 
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
