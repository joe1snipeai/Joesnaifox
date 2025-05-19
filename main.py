import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

DEXSCREENER_SOLANA_URL = "https://api.dexscreener.com/latest/dex/pairs/solana"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ALLOWED_USER_ID = os.getenv("TELEGRAM_USER_ID")  # Only allow this user

token_states = {}
SLEEP_INTERVAL = 10

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=data)

def monitor():
    while True:
        try:
            r = requests.get(DEXSCREENER_SOLANA_URL)
            if r.status_code == 200:
                data = r.json().get("pairs", [])
                for pair in data:
                    addr = pair.get("pairAddress")
                    name = pair.get("baseToken", {}).get("name", "")
                    symbol = pair.get("baseToken", {}).get("symbol", "")
                    promoted = pair.get("isPromoted", False)
                    lp = pair.get("liquidity", {}).get("usd", 0)
                    tx = pair.get("txCount", {}).get("m5", 0)
                    age_min = (int(time.time()*1000) - pair.get("pairCreatedAt", 0)) // 60000

                    if addr not in token_states:
                        token_states[addr] = {"name": name, "symbol": symbol, "isPromoted": promoted}
                        continue

                    old = token_states[addr]

                    if old["name"] == "" and name != "":
                        msg = f"**SETUP DETECTED**\n{name} ({symbol})\nLP: ${lp:.2f}, TX: {tx}, Age: {age_min:.1f}min\n[Chart](https://dexscreener.com/solana/{addr})"
                        send_telegram_message(msg)

                    if not old["isPromoted"] and promoted:
                        msg = f"**PROMOTED**\n{name} ({symbol}) now promoted on DexScreener!\nLP: ${lp:.2f}, TX: {tx}, Age: {age_min:.1f}min\n[Chart](https://dexscreener.com/solana/{addr})"
                        send_telegram_message(msg)

                    token_states[addr] = {"name": name, "symbol": symbol, "isPromoted": promoted}
        except Exception as e:
            print("Eroare:", e)
        time.sleep(SLEEP_INTERVAL)

monitor()
