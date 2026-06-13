import requests
import json
from bs4 import BeautifulSoup

def get_next_race(horse_id):

    url = "https://db.netkeiba.com/social/api_db_horse_info_simple.html"

    params = {
        "input": "UTF-8",
        "output": "json",
        "id": horse_id
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://db.netkeiba.com/horse/{horse_id}/"
    }

    try:

        r = requests.get(
            url,
            params=params,
            headers=headers
        )

        html = json.loads(r.text)

        soup = BeautifulSoup(html, "html.parser")

        box = soup.find("div", class_="next_race_data_box_01")

        if box is None:
            return "未定"

        dd = box.find("dd")

        date_text = dd.contents[0].strip()

        race_name = box.find(
            "span",
            class_="race_name"
        ).get_text(strip=True)

        return f"{date_text} {race_name}"

    except:
        return "未定"


print("クロワデュノール")
print(get_next_race("2022105102"))

print()

print("レイピア")
print(get_next_race("2022103066"))