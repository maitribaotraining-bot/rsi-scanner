from vnstock import Vnstock
import pandas as pd
import ta
import requests
import time
import os

# ====================================
# TELEGRAM
# ====================================

BOT_TOKEN = "8937864972:AAGOMsxZOG7s6bKVW1al93ahQcfWU3lUYUg"
CHAT_ID = "1259162767"

# ====================================
# DANH SACH MA
# ====================================

hose_symbols = [
    "HPG","SSI","VCI","VND","HCM","MBB","TCB","VPB",
    "FPT","MWG","STB","SHB","CTG","VCB","BID","VIC",
    "VHM","VRE","DXG","DIG","NLG","PDR","KDH","GEX",
    "REE","POW","GAS","PLX","DBC","DGC","KBC","ANV",
    "ASM","CSV","CTR","DPM","DCM","EIB","EVF","FTS",
    "GMD","HAG","HSG","IJC","KSB","LCG","MSN","NVL",
    "OCB","PC1","PNJ","PVT","SBT","SCR","SZC","TPB",
    "VCG","VHC","VIX","VOS"
]

# ====================================
# CAU HINH BATCH
# ====================================

BATCH_SIZE = 10
STATE_FILE = "batch.txt"

# ====================================
# DOC VI TRI BATCH
# ====================================

if os.path.exists(STATE_FILE):

    with open(STATE_FILE, "r") as f:
        start_index = int(f.read())

else:

    start_index = 0

end_index = start_index + BATCH_SIZE

batch_symbols = hose_symbols[start_index:end_index]

# RESET VE DAU
if len(batch_symbols) == 0:

    start_index = 0
    end_index = BATCH_SIZE

    batch_symbols = hose_symbols[start_index:end_index]

# ====================================
# GUI TELEGRAM BAT DAU
# ====================================

requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": f"🚀 Scan batch {start_index} -> {end_index}"
    }
)

signals = []

# ====================================
# HAM RSI
# ====================================

def get_rsi(df):

    close = pd.to_numeric(df["close"])

    rsi = ta.momentum.RSIIndicator(
        close=close,
        window=14
    ).rsi()

    return round(rsi.iloc[-1], 2)

# ====================================
# QUET
# ====================================

for symbol in batch_symbols:

    try:

        print("Scanning:", symbol)

        stock = Vnstock().stock(
            symbol=symbol,
            source="VCI"
        )

        df = stock.quote.history(
            start="2024-01-01",
            end="2026-12-31",
            interval="1D"
        )

        if df is None or len(df) < 20:
            continue

        latest_rsi = get_rsi(df)

        latest_price = round(
            pd.to_numeric(df["close"]).iloc[-1],
            2
        )

        print(symbol, latest_rsi)

        # DIEU KIEN RSI
        if latest_rsi < 30:

            signals.append(
                f"🟢 {symbol}\n"
                f"Gia: {latest_price}\n"
                f"RSI14: {latest_rsi}\n"
            )

        # CHONG LIMIT
        time.sleep(4)

    except Exception as e:

        print(symbol, e)

        time.sleep(6)

# ====================================
# TAO NOI DUNG
# ====================================

if signals:

    message = (
        f"📉 Batch {start_index} -> {end_index}\n\n"
        + "\n".join(signals)
    )

else:

    message = (
        f"❌ Batch {start_index} -> {end_index}\n"
        f"Khong co ma RSI14 < 30"
    )

# ====================================
# GUI TELEGRAM
# ====================================

requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

# ====================================
# LUU BATCH TIEP
# ====================================

next_index = end_index

if next_index >= len(hose_symbols):

    next_index = 0

with open(STATE_FILE, "w") as f:

    f.write(str(next_index))

print("DONE")
