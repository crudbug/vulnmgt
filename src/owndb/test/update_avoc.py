import datetime
import hmac
import os
from os.path import join, abspath, dirname
import sys
import json
import base64
from hashlib import sha256

import requests

here = lambda *x: join(abspath(dirname(__file__)), *x)
PROJECT_ROOT = here("..")
sys.path.append(PROJECT_ROOT)


AVOC_ENDPOINT = 'http://127.0.0.1:8000/sapi/avoc/'
HMAC_KEY = ''
payload = {
    "avoc_state_msg": "not vulnerable",
    "avoc_scan_date": "2014-12-12",
}
payload = json.dumps(payload)
hmac_digest = hmac.new(
    base64.b64decode(HMAC_KEY),
    payload.encode('utf-8'),
    sha256).hexdigest()
payload = {'sdata': payload, 'hmac': hmac_digest}
r = requests.patch(AVOC_ENDPOINT + '7089/',
        data=payload,
        verify=False)
print r.text
print r.json()

