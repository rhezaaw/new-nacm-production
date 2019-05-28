"""
WSGI config for nacm project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import time 
import traceback 
import signal 
import sys 
import site

from django.core.wsgi import get_wsgi_application
# site.addsitedir('/var/www/NACM/venv/lib/python3.6/site-packages')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nacm.settings')

application = get_wsgi_application()

# sys.path.append('/var/www/NACM') 
# # adjust the Python version in the line below as needed 
# sys.path.append('/var/www/NACM/venv/lib/python3.6/site-packages') 
 
# # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings") 
 
# try: 
#     application = get_wsgi_application() 
# except Exception: 
#     # Error loading applications 
#     if 'mod_wsgi' in sys.modules: 
#         traceback.print_exc() 
#         os.kill(os.getpid(), signal.SIGINT) 
#         time.sleep(2.5) 