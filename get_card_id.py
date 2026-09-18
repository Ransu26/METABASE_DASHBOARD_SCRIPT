import requests

url = "http://localhost:3000/api/card"
headers = {
    "x-api-Key": ""
}

response = requests.get(url, headers=headers)
cards = response.json()

# Print each question's ID and Name
for card in cards:
    print(f"Card ID: {card['id']} | Name: {card['name']}")