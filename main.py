```python
from vnstock import stock_historical_data
import ta
import requests

BOT_TOKEN = "8937864972:AAGOMsxZOG7s6bKVW1al93ahQcfWU3lUYUg"
CHAT_ID = "1259162767"

# GUI BAT DAU
requests.get(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    params={
        "chat_id": CHAT_ID,
        "text": "🚀 BAT DAU SCAN RSI"
    }
)

# DANH SACH MA
hose_symbols = [
    "AAA","AAM","ABR","ABS","ABT","ACB","ACC","ACL","ADS","AGG",
    "AGR","ANV","APG","APH","ASM","AST","BCG","BCM","BFC","BIC",
    "BID","BMI","BMP","BSI","BTP","BWE","C32","C47","CAV","CCI",
    "CCL","CDC","CHP","CIG","CMG","CMX","CNG","COM","CRC","CSM",
    "CTD","CTG","CTR","CTS","CVT","DBC","DBD","DCM","DGC","DGW",
    "DHA","DHC","DIG","DMC","DPM","DRC","DXG","DXS","EIB","ELC",
    "EVF","FCN","FPT","FRT","FTS","GAS","GEX","GIL","GMD","GVR",
    "HAG","HAH","HAX","HCM","HDB","HDG","HHS","HHV","HPG","HSG",
    "HT1","HVN","IDI","IJC","IMP","KBC","KDC","KDH","KOS","LCG",
    "LPB","MBB","MSB","MSN","MWG","NKG","NLG","NT2","OCB","ORS",
    "PAN","PC1","PDR","PET","PHR","PLX","PNJ","POW","PTB","PVD",
    "PVT","REE","SAB","SAM","SBT","SCR","SHB","SJS","SSI","STB",
    "SZC","TCB","TCH","TLG","TPB","VCB","VCG","VCI","VDS","VGC",
    "VHC","VHM","VIB","VIC","VIX","VND","VNM","VPB","VPG","VPI",
    "VRE","VSC","VSH","YEG","APH","ASM","BAF","BAF","BWE","CMG",
    "CTR","CSV","D2D","DPR","DRH","EVG","FIR","GEE","GVR","HDC",
    "HNG","ITA","KHG","LHG","MIG","NHA","NTL","OGC","PGC","QCG",
    "RAL","SCS","SGN","TDM","TIP","TV2","VCF","VHC","VOS","VTO"
]

signals = []

# HAM TINH RSI
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

# QUET
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

        # DIEU KIEN
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

# TIN NHAN
if signals:

    message = "\n".join(signals)

else:

    message = "❌ KHONG CO MA THOA DIEU KIEN"

# GUI TELEGRAM
response = requests.get(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    params={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(response.text)

# HOAN TAT
requests.get(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    params={
        "chat_id": CHAT_ID,
        "text": "✅ SCAN HOAN TAT"
    }
)
```
