import requests

api_url = "https://bible-api.com/"
verse="mark6:13"

response = requests.get(api_url + verse)
data = response.json()
print(data["text"])