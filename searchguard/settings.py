import os

HEADER = {'content-type': 'application/json'}
SGAPI = os.environ.get('SEARCHGUARD_API_URL', '')
TOKEN = (os.environ.get('SEARCHGUARD_API_USER', ''), os.environ.get('SEARCHGUARD_API_PASS', ''))
