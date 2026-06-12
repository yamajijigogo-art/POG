import requests

url = "https://db.netkeiba.com/horse/2022105102/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

text = response.text

for word in [
    "宝塚記念",
    "近況",
    "阪神",
    "2026/6/14"
]:
    print(word, "=>", text.find(word))