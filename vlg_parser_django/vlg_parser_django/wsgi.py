"""
WSGI config for vlg_parser_django project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.append('/root/workspace/vlg_parser/source/vlg_parser_django')
sys.path.append('/root/workspace/vlg_parser/.py_env/lib/python3.6/site-packages')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vlg_parser_django.settings')

application = get_wsgi_application()