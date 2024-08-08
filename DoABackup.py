# use python to GET api 
import requests
import json
import time
import base64

url = 'http://localhost:3000/api/database/backup'
APIKey = 'TheAPIKeyOfLANraragi'

# This key must be added to your calls as an Authorization: Bearer header, with the key encoded in base64
# encode the key in base64
APIKey_base64 = base64.b64encode(APIKey.encode('utf-8')).decode('utf-8')
headers = {
    'Authorization': 'Bearer ' + APIKey_base64
}
response = requests.get(url, headers=headers)

# save the response data as json
data = response.json()
# current date and time
datetime = time.strftime("%Y%m%dT%H%M%S", time.localtime())
with open(f'backup_{datetime}.json', 'w') as f:
    json.dump(data, f, indent=4)