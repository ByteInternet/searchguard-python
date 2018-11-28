import os

HEADER = {'content-type': 'application/json'}
SEARCHGUARD_API_URL = os.environ.get('SEARCHGUARD_API_URL', '')
SEARCHGUARD_API_AUTH = (os.environ.get('SEARCHGUARD_API_USER', ''), os.environ.get('SEARCHGUARD_API_PASS', ''))
