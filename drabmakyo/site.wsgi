import os
import sys

path = "/home/makyo/sites/drabmakyo"
if not path in sys.path:
    sys.path.append(path)
    os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

# vim: ft=python
