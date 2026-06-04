from vnstock import *
import ta
import requests

BOT_TOKEN = "8937864972:AAGOMsxZOG7s6bKVW1al93ahQcfWU3lUYUg"
CHAT_ID = "1259162767"

requests.get(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    params={
        "chat_id": CHAT_ID,
        "text": "🚀 BAT DAU SCAN RSI"
    }
)

companies = listing_companies()

hose_symbols = companies[
    companies["exchange"] == "HOSE"
]["ticker"].tolist()

signals = []

def get_indicators(df):

    rsi = ta.momentum.RSIIndicator(
        close=df["close"],
        window=14
    ).rsi()

    stoch = ta.momentum.StochRSIIndicator(
        close=df["close"],
        window=14,
        smooth1=3,
        smooth2=3
    )

    latest_rsi = round(rsi.iloc[-1], 2)

    latest_stoch = round(
        stoch.stochrsi_k().iloc[-1] * 100,
        2
    )

    return latest_rsi, latest_stoch

for symbol in hose_symbols:

    try:

        print("Dang quet:", symbol)

        df = stock_historical_data(
            symbol=symbol,
            start_date="2025-01-01",
            end_date="2026-12-31",
            resolution="1D",
            type="stock",
            beautify=True,
            decor=False,
            source="DNSE"
        )

        if len(df) < 50:
            continue

        rsi_1d, stoch_1d = get_indicators(df)

        print(symbol, rsi_1d, stoch_1d)

        if rsi_1d < 30 and stoch_1d < 30:

            latest_price = df["close"].iloc[-1]

            signals.append(
                f"🟢 {symbol}\n"
                f"Gia: {latest_price}\n"
                f"RSI14 1D: {rsi_1d}\n"
                f"Stoch RSI 1D: {stoch_1d}\n"
            )

    except Exception as e:

        print("LOI:", symbol, e)

if signals:

    message = "\n".join(signals)

else:

    message = "❌ KHONG CO MA HOSE THOA DIEU KIEN"

response = requests.get(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    params={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(response.text)

requests.get(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    params={
        "chat_id": CHAT_ID,
        "text": "✅ SCAN HOAN TAT"
    }
)
