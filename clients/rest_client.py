import requests
import json
from unicode_utils import unicode_to_string

auth = ('user', 'password')
auth = None
url = 'http://localhost:8080/dvr/recordings'

response = requests.get(url, auth=auth)
data = response.json()

print "data: ", data

dvr_entry = {'channel': 'My channel'}

response = requests.post(url, json.dumps(dvr_entry), auth=auth)
print "response: ", response
print "response.content: ", response.content
data = unicode_to_string(response.json())
print "data: ", data
