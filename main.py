from vnstock import Vnstock
import pandas as pd
import ta
import requests
import traceback

# ==============================
# TELEGRAM
# ==============================

BOT_TOKEN = "8937864972:AAGOMsxZOG7s6bKVW1al93ahQcfWU3lUYUg"
CHAT_ID = "1259162767"

# ==============================
# VNSTOCK
# ==============================

stock = Vnstock().stock(
    symbol='VCB',
    source='VCI'
)

# ==============================
# LẤY TOÀN BỘ MÃ HOSE
# ==============================

try:
    companies = stock.listing.symbols_by_exchange()

    hose_symbols = companies[
        companies['exchange'] == 'HOSE'
    ]['symbol'].tolist()

except:
    # fallback nếu lỗi API
    hose_symbols = [
        'HPG','SSI','VCI','VND','HCM','MBB','TCB','VPB',
        'FPT','MWG','STB','SHB','CTG','VCB','BID','VIC',
        'VHM','VRE','DXG','DIG'
    ]

signals = []

# ==============================
# QUÉT RSI
# ==============================

for symbol in hose_symbols:

    try:

        data = Vnstock().stock(
            symbol=symbol,
            source='VCI'
        )

        df = data.quote.history(
            start='2024-01-01',
            end='2026-12-31',
            interval='1D'
        )

        if df is None or len(df) < 20:
            continue

        close = pd.to_numeric(df['close'])

        # RSI 14
        rsi = ta.momentum.RSIIndicator(
            close=close,
            window=14
        ).rsi()

        latest_rsi = round(rsi.iloc[-1], 2)

        # ĐIỀU KIỆN
        if latest_rsi < 30:

            latest_price = round(close.iloc[-1], 2)

            signals.append(
                f"🟢 {symbol}\n"
                f"Giá: {latest_price}\n"
                f"RSI14 1D: {latest_rsi}\n"
            )

    except Exception as e:
        print(symbol, e)

# ==============================
# TẠO MESSAGE
# ==============================

if signals:

    message = (
        "📉 RSI14 < 30 HOSE\n\n"
        + "\n".join(signals[:200])
    )

else:

    message = "❌ Không có mã HOSE RSI14 < 30"

print(message)

# ==============================
# GỬI TELEGRAM
# ==============================

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

response = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(response.text)
