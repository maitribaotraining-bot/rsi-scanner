from vnstock import Vnstock
import pandas as pd
import ta
import requests
import time

BOT_TOKEN = "8937864972:AAGOMsxZOG7s6bKVW1al93ahQcfWU3lUYUg"
CHAT_ID = "1259162767"

hose_symbols = [
    "HPG","SSI","VCI","VND","HCM","MBB","TCB","VPB",
    "FPT","MWG","STB","SHB","CTG","VCB","BID","VIC",
    "VHM","VRE","DXG","DIG","NLG","PDR","KDH","GEX",
    "REE","POW","GAS","PLX","DBC","DGC","KBC","ANV"
]

signals = []

for i, symbol in enumerate(hose_symbols):

    try:

        print(f"Scanning {symbol}")

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

        close = pd.to_numeric(df["close"])

        rsi = ta.momentum.RSIIndicator(
            close=close,
            window=14
        ).rsi()

        latest_rsi = round(rsi.iloc[-1], 2)

        if latest_rsi < 30:

            latest_price = round(close.iloc[-1], 2)

            signals.append(
                f"{symbol} | Gia: {latest_price} | RSI14: {latest_rsi}"
            )

        # chống limit
        time.sleep(5)

    except Exception as e:

        print(symbol, e)

        # nghỉ lâu hơn nếu lỗi
        time.sleep(10)

if signals:

    message = "📉 RSI14 < 30\n\n" + "\n".join(signals)

else:

    message = "❌ Khong co ma RSI14 < 30"

requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(message)
