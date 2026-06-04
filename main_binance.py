import requests
from bs4 import BeautifulSoup

BOT_TOKEN = "8789985536:AAG5d_wzvzzNN_cVFevFPGuj8MEZOmphfpE"
CHAT_ID = "1259162767"

url = "https://www.binance.com/en/support/announcement/c-48"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    url,
    headers=headers
)

html = response.text

soup = BeautifulSoup(
    html,
    "html.parser"
)

text = soup.get_text()

keywords = [
    "delist",
    "delisting",
    "remove"
]

found = []

for line in text.split("\n"):

    line = line.strip()

    if len(line) < 20:
        continue

    lower = line.lower()

    for keyword in keywords:

        if keyword in lower:

            found.append(line)

            break

# XOA TRUNG
found = list(set(found))

# MESSAGE
if found:

    message = "🚨 BINANCE DELIST ALERT 🚨\n\n"

    for item in found[:10]:

        message += f"{item}\n\n"

else:

    message = "✅ Không có tin delist mới"

# GUI TELEGRAM
requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(message)
