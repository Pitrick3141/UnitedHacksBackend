import requests

base_url = 'https://api.pitrick.link/united-hacks/'
resource = 'test'

res = requests.get(base_url + resource)

print(res.text)
