```python
from vnstock import *
import pandas as pd
import ta
import requests

# ==============================
# TELEGRAM
# ==============================

BOT_TOKEN = "8937864972:AAGOMsxZOG7s6bKVW1al93ahQcfWU3lUYUg"
CHAT_ID = "1259162767"

# ==============================
# LẤY DANH SÁCH HOSE
# ==============================

companies = listing_companies()

hose_symbols = companies[
    companies['exchange'] == 'HOSE'
]['ticker'].tolist()

signals = []

# ==============================
# HÀM TÍNH RSI + STOCH RSI
# ==============================

def get_indicators(df):

    # RSI14
    rsi = ta.momentum.RSIIndicator(
        close=df['close'],
        window=14
    ).rsi()

    latest_rsi = round(
        rsi.iloc[-1],
        2
    )

    # STOCH RSI
    stoch = ta.momentum.StochRSIIndicator(
        close=df['close'],
        window=14,
        smooth1=3,
        smooth2=3
    )

    latest_stoch = round(
        stoch.stochrsi_k().iloc[-1] * 100,
        2
    )

    return latest_rsi, latest_stoch

# ==============================
# QUÉT TOÀN BỘ HOSE
# ==============================

for symbol in hose_symbols:

    try:

        df = stock_historical_data(
            symbol=symbol,
            start_date="2025-01-01",
            end_date="2026-12-31",
            resolution='1D',
            type='stock',
            beautify=True,
            decor=False,
            source='DNSE'
        )

        # BỎ QUA MÃ KHÔNG ĐỦ DỮ LIỆU
        if len(df) < 50:
            continue

        # ==============================
        # RSI + STOCH RSI 1D
        # ==============================

        rsi_1d, stoch_1d = get_indicators(df)

        # ==============================
        # ĐIỀU KIỆN LỌC
        # ==============================

        if (
            rsi_1d < 30
            and stoch_1d < 30
        ):

            latest_price = df['close'].iloc[-1]

            signals.append(
                f"""
🟢 {symbol}
Giá: {latest_price}
RSI14 1D: {rsi_1d}
Stoch RSI 1D: {stoch_1d}
"""
            )

    except Exception as e:

        print(symbol, e)

# ==============================
# TẠO NỘI DUNG TELEGRAM
# ==============================

if signals:

    message = "\n".join(signals)

else:

    message = "Không có mã HOSE thỏa điều kiện"

# ==============================
# GỬI TELEGRAM
# ==============================

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(message)
```

