import json 
import requests

def get_token(url, body):
    response = requests.post(url + "connect", data=body)
    return json.loads(response.text)['access_token']
