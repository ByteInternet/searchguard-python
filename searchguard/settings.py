import os

HEADER = {'content-type': 'application/json'}
SGAPI = os.environ['SEARCHGUARD_API_URL']
TOKEN = (os.environ['SEARCHGUARD_API_USER'], os.environ['SEARCHGUARD_API_PASS'])
