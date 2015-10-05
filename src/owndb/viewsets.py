import base64
import hmac
import json
from hashlib import sha256

from django.conf import settings
from issuesdb.api.viewsets import BaseModelViewSet as IssuesdbBaseModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.response import Response


class HMACPermissionMixin(object):
    def check_permissions(self, request):
        """
        We have to different permission schemes. HMAC signature and normal auth.
        """
        if not hasattr(settings, 'HMAC_KEY'):
            super(HMACPermissionMixin, self).check_permissions(request)

        if (('hmac' in request.REQUEST and 'sdata' in request.REQUEST) or
                ('hmac' in request.DATA and 'sdata' in request.DATA)):
            sdata = request.REQUEST.get('sdata') or request.DATA.get('sdata')
            data_hmac = request.REQUEST.get('hmac') or request.DATA.get('hmac')

            if data_hmac.lower().strip() != hmac.new(
                    base64.b64decode(settings.HMAC_KEY),
                    sdata.encode('utf-8'),
                    sha256).hexdigest():
                self.permission_denied(request)
            try:
                data = json.loads(sdata)
                if isinstance(data, dict):
                    request._data = request.data.copy() # make querydict mutable
                    request.data.update(data)
            except ValueError:
                pass
        else:
            super(HMACPermissionMixin, self).check_permissions(request)


class BaseModelViewSet(HMACPermissionMixin, IssuesdbBaseModelViewSet):
    pass


class SeverityViewSet(HMACPermissionMixin, ListAPIView):
    def list(self, request, *args, **kwargs):
        return Response([{"id": t[0], "name": t[1]} for t in settings.ISSUE_SEVERITY_CHOICES])

    def get_queryset(self):
        return None


