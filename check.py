from datetime import datetime

import json
import os
import requests

from bs4 import BeautifulSoup

URL = "https://yan-flash.com/ultimate/yosei-ranbu"

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

SAVE_FILE = "last_updates.json"


def send_discord(message):
    response = requests.post(
        WEBHOOK_URL,
        json={
            "content": message
        },
        timeout=30
    )

    response.raise_for_status()


def load_updates():
    try:
        with open(
            SAVE_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except FileNotFoundError:
        return []


def save_updates(data):
    with open(
        SAVE_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def get_current_updates():

    response = requests.get(
        URL,
        timeout=30,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64)"
            )
        }
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    section = soup.select_one(
        "#ult-changelog"
    )

    if section is None:
        raise Exception(
            "ult-changelog が見つかりません"
        )

    items = []

    for li in section.select("li"):

        time_tag = li.find("time")
        p_tag = li.find("p")

        if not time_tag or not p_tag:
            continue

        items.append({
            "time": time_tag.get_text(
                strip=True
            ),
            "text": p_tag.get_text(
                strip=True
            )
        })

    return items


def create_message(new_items):

    lines = []

    for item in reversed(new_items):

        lines.append(
            f"🕒 {item['time']}"
        )

        lines.append(
            item["text"]
        )

        lines.append("")

    body = "\n".join(lines)

    return (
        "🚨 妖精乱舞 更新検知\n\n"
        f"{body}\n"
        f"{URL}"
    )


def main():

    print(
        f"Monitor started: {datetime.now()}"
    )
    
    current_items = get_current_updates()

    old_items = load_updates()

    old_set = {
        (
            item["time"],
            item["text"]
        )
        for item in old_items
    }

    new_items = [
        item
        for item in current_items
        if (
            item["time"],
            item["text"]
        ) not in old_set
    ]

    if not old_items:

        save_updates(
            current_items
        )

        print(
            "初回実行のため保存のみ"
        )

        return

    if new_items:

        message = create_message(
            new_items
        )

        send_discord(
            message
        )

        print(
            f"{len(new_items)}件の更新を通知"
        )

    else:

        print(
            "更新なし"
        )

    save_updates(
        current_items
    )


if __name__ == "__main__":
    main()
