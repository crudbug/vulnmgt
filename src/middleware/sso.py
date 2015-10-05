from __future__ import unicode_literals
from django.contrib.auth.middleware import RemoteUserMiddleware


class SAPOSSOHeaderMiddleware(RemoteUserMiddleware):
    header = 'HTTP_SSOMAIL'

