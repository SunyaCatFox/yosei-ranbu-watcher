import hashlib
import os
import requests

from bs4 import BeautifulSoup

URL = "https://yan-flash.com/ultimate/yosei-ranbu"

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

HASH_FILE = "last_hash.txt"


def send_discord(message):
    requests.post(
        WEBHOOK_URL,
        json={
            "content": message
        },
        timeout=30
    )


def load_hash():
    if not os.path.exists(HASH_FILE):
        return ""

    with open(HASH_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_hash(value):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        f.write(value)


def main():

    response = requests.get(
        URL,
        timeout=30
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
            "ult-changelogが見つかりません"
        )

    content = section.get_text(
        separator="\n",
        strip=True
    )

    current_hash = hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

    old_hash = load_hash()

    if old_hash == "":
        save_hash(current_hash)
        print("初回実行")
        return

    """
    if current_hash != old_hash:

        send_discord(
            "🚨 妖精乱舞の更新履歴が更新されました！\n"
            f"{URL}"
        )

        save_hash(current_hash)

        print("更新検知")

    else:
        print("変更なし")
    """
    
    send_discord(
    "🧪 GitHub Actions テスト通知"
    )

    save_hash(current_hash)


if __name__ == "__main__":
    main()
