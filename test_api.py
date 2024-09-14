import requests
import json

url = "http://localhost:5000/generate"
payload = {
       "prompt": "A serene lake surrounded by mountains at night",
       "width": 512,
       "height": 512,
       "steps": 20,
       "guidance": 7.5,
       "seed": 42
   }
headers = {"Content-Type": "application/json"}

response = requests.post(url, data=json.dumps(payload), headers=headers)
print(json.dumps(response.json(), indent=2))