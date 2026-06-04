from vnstock import Vnstock
import pandas as pd
import ta
import requests
import time

# ======================================
# TELEGRAM
# ======================================

BOT_TOKEN = "8937864972:AAGOMsxZOG7s6bKVW1al93ahQcfWU3lUYUg"
CHAT_ID = "1259162767"

# ======================================
# DANH SÁCH MÃ HOSE
# ======================================

hose_symbols = [
    "HPG","SSI","VCI","VND","HCM","MBB","TCB","VPB",
    "FPT","MWG","STB","SHB","CTG","VCB","BID","VIC",
    "VHM","VRE","DXG","DIG","NLG","PDR","KDH","GEX",
    "REE","POW","GAS","PLX","DBC","DGC","KBC","ANV",
    "ASM","CSV","CTR","DPM","DCM","EIB","EVF","FTS",
    "GMD","HAG","HSG","IJC","KSB","LCG","MSN","NVL",
    "OCB","PC1","PNJ","PVT","SBT","SCR","SZC","TPB",
    "VCG","VHC","VIX","VOS","AAA","ABB","ACB","APH",
    "BCM","BMP","BSI","BVH","CII","CMG","CRE","CSM",
    "CTD","CTS","CVT","D2D","DGW","DHG","DPR","DRC",
    "DXS","FRT","GIL","HDG","HHV","HVN","IDI","IJC",
    "KOS","LPB","MIG","MSB","NKG","NT2","PAN","PET",
    "PHR","PVD","PVS","RAL","SAM","SCS","SGN","TCH",
    "TLG","VCF","VIB","VPI","YEG"
]

signals = []

# ======================================
# QUÉT RSI
# ======================================

for i, symbol in enumerate(hose_symbols):

    try:

        print(f"Scanning {symbol} ({i+1}/{len(hose_symbols)})")

        stock = Vnstock().stock(
            symbol=symbol,
            source='VCI'
        )

        df = stock.quote.history(
            start='2024-01-01',
            end='2026-12-31',
            interval='1D'
        )

        if df is None or len(df) < 20:
            continue

        close = pd.to_numeric(df['close'])

        # RSI14
        rsi = ta.momentum.RSIIndicator(
            close=close,
            window=14
        ).rsi()

        latest_rsi = round(rsi.iloc[-1], 2)

        # ĐIỀU KIỆN RSI < 30
        if latest_rsi < 30:

            latest_price = round(close.iloc[-1], 2)

            signals.append(
                f"🟢 {symbol}\n"
                f"Giá: {latest_price}\n"
                f"RSI14 1D: {latest_rsi}\n"
            )

        # CHỐNG RATE LIMIT
        time.sleep(3)

    except Exception as e:

        print(f"Lỗi {symbol}: {e}")

        # nếu lỗi thì nghỉ thêm
        time.sleep(5)

# ======================================
# MESSAGE
# ======================================

if signals:

    message = (
        "📉 DANH SÁCH RSI14 < 30\n\n"
        + "\n".join(signals)
    )

else:

    message = "❌ Không có mã RSI14 < 30"

print(message)

# ======================================
# GỬI TELEGRAM
# ======================================

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

response = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(response.text)
