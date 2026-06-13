import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import json

st.title("POG 2026")

if st.button("🔄 最新データ取得"):
    st.cache_data.clear()

df = pd.read_csv("horses.csv")


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
            headers=headers,
            timeout=10
        )

        html = json.loads(r.text)

        soup = BeautifulSoup(html, "html.parser")

        box = soup.find("div", class_="next_race_data_box_01")

        if box is None:
            return "未定"

        dd = box.find("dd")

        date_text = dd.contents[0].strip()

        date_text = date_text.split("(")[0]

        parts = date_text.split("/")

        date_text = f"{parts[1]}/{parts[2]}"

        race_name = box.find(
            "span",
            class_="race_name"
        ).get_text(strip=True)

        return f"{date_text} {race_name}"

    except:
        return "未定"


@st.cache_data(ttl=3600)
def get_data():

    results = []

    for _, row in df.iterrows():

        url = row["url"]

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        horse_name = soup.title.text
        horse_name = horse_name.split("|")[0]
        horse_name = horse_name.split("(")[0]
        horse_name = horse_name.strip()

        text = soup.get_text()

        m = re.search(
            r'獲得賞金 \(中央\)\s*([\d億万円,]+)',
            text
        )
        prize = m.group(1) if m else "取得失敗"

        m2 = re.search(
            r'通算成績\s*([0-9戦勝\[\]\- ]+)',
            text
        )
        record = m2.group(1) if m2 else "取得失敗"

        record = record.split("[")[0].strip()

        prize_num = 0

        if "億" in prize:
            oku, man = prize.replace(
                "万円",
                ""
            ).split("億")

            prize_num = (
                int(oku) * 10000
                + int(man.replace(",", ""))
            )

        else:
            prize_num = int(
                prize.replace("万円", "")
                .replace(",", "")
            )

        horse_id = (
            url.rstrip("/")
            .split("/")[-1]
        )

        next_race = get_next_race(horse_id)

        results.append({
            "owner": row["owner"],
            "馬名": horse_name,
            "賞金": prize,
            "賞金数値": prize_num,
            "戦績": record,
            "次走": next_race
        })

    return pd.DataFrame(results)


result_df = get_data()

my_total = (
    result_df[result_df["owner"] == "A"]
    ["賞金数値"]
    .sum()
)

friend_total = (
    result_df[result_df["owner"] == "B"]
    ["賞金数値"]
    .sum()
)

ranking = pd.DataFrame({
    "オーナー": ["A", "B"],
    "総賞金(万円)": [
        my_total,
        friend_total
    ]
})

ranking = ranking.sort_values(
    "総賞金(万円)",
    ascending=False
)

st.header("🏆順位表")

st.dataframe(
    ranking,
    use_container_width=True
)

st.header("🔥賞金ランキング TOP5")

top5 = result_df.sort_values(
    "賞金数値",
    ascending=False
).head(5)

st.dataframe(
    top5[["馬名", "賞金", "戦績"]],
    use_container_width=True
)

st.header("A")

a_df = result_df[
    result_df["owner"] == "A"
].copy()


for _, row in a_df.iterrows():

    horse_url = df[
        (df["owner"] == "A")
        & (df["horse"] == row["馬名"])
    ]["url"].iloc[0]

    st.markdown(
        f"""
### 🐴 [{row["馬名"]}]({horse_url})

**賞金**：{row["賞金"]}

**戦績**：{row["戦績"]}

**次走**：{row["次走"]}

---
"""
    )

st.header("B")

b_df = result_df[
    result_df["owner"] == "B"
].copy()

b_df["馬名"] = [
    f'<a href="{url}" target="_blank">{horse}</a>'
    for horse, url in zip(
        df[df["owner"] == "B"]["horse"],
        df[df["owner"] == "B"]["url"]
    )
]

st.write(
    b_df[
        ["馬名", "賞金", "戦績", "次走"]
    ].to_html(
        escape=False,
        index=False
    ),
    unsafe_allow_html=True
)
