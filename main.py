from vnstock import Vnstock
import pandas as pd
import ta
import requests
import time
import numpy as np
from datetime import datetime

# ====================================
# TELEGRAM CONFIG
# ====================================
BOT_TOKEN = "8937864972:AAGOMsxZOG7s6bKVW1al93ahQcfWU3lUYUg"
CHAT_ID = "-1004292489803"

# ====================================
# DANH SACH 200 MA POTENTIAL
# ====================================
hose_symbols = [
    "HPG", "SSI", "VCI", "VND", "HCM", "MBB", "TCB", "VPB",
    "FPT", "MWG", "STB", "SHB", "CTG", "VCB", "BID", "VIC",
    "VHM", "VRE", "DXG", "DIG", "NLG", "PDR", "KDH", "GEX",
    "REE", "POW", "GAS", "PLX", "DBC", "DGC", "KBC", "ANV",
    "ASM", "CSV", "CTR", "DPM", "DCM", "EIB", "EVF", "FTS",
    "GMD", "HAG", "HSG", "IJC", "KSB", "LCG", "MSN", "NVL",
    "OCB", "PC1", "PNJ", "PVT", "SBT", "SCR", "SZC", "TPB",
    "VCG", "VHC", "VIX", "VOS", "ACB", "HDB", "VIB", "LPB",
    "MSB", "SSB", "BSI", "TXT", "ORS", "AGR", "SHS", "MBS",
    "BVS", "VDS", "NKG", "TLH", "SMC", "POM", "VGS", "TVN",
    "CEO", "L14", "CII", "HUT", "NHA", "TCH", "KHG", "DXS",
    "IDC", "ITA", "GVR", "BCM", "VGC", "TIP", "LHG", "D2D",
    "NTL", "SJS", "HDG", "QCG", "AGG", "BCG", "CRE", "HQC",
    "PVD", "PVS", "OIL", "BSR", "PVC", "TV2", "GEG", "QTP",
    "HND", "HHV", "FCN", "C4G", "G36", "HT1", "BCC", "DHA",
    "FRT", "DGW", "PET", "VNM", "SAB", "BHN", "MCH", "KDC",
    "VCF", "BAF", "VLC", "PAN", "TLG", "HAT", "CLC", "IMP",
    "BFC", "LAS", "PHR", "DPR", "TRC", "DRI", "HNG", "AAA",
    "APH", "VHG", "HAH", "VSC", "MVN", "VIP", "VTO", "IDI",
    "FMC", "CMX", "ACL", "MPC", "AST", "SAS", "ACV", "VGI",
    "FOX", "ELC", "CMG", "BMP", "NTP", "TRA", "DHT", "DBD",
    "TNG", "MSH", "TCM", "GIL", "VGT", "VEA", "VEF", "VTP",
    "SCS", "BVB", "NAB", "PGB", "ABB", "VBB", "NVB", "BAB",
    "KLB", "TSA", "TCI", "PSI", "IVS", "APG", "TVB", "TVS",
    "VFS", "SBS", "AAS", "DSC", "PAS", "DTL", "BCA", "VIS"
]

# ====================================
# TỰ ĐỘNG TÍNH TOÁN BATCH
# ====================================
BATCH_SIZE = 10
total_slots = len(hose_symbols) // BATCH_SIZE

current_minute = datetime.now().minute
current_hour = datetime.now().hour

total_runs_today = (current_hour * 4) + (current_minute // 15)
batch_index = total_runs_today % total_slots
group_number = batch_index + 1 

start_index = batch_index * BATCH_SIZE
end_index = start_index + BATCH_SIZE
batch_symbols = hose_symbols[start_index:end_index]

def send_telegram(text_message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text_message,
            "parse_mode": "Markdown"
        }
        requests.post(url, data=payload)
    except Exception as e:
        print("Lỗi gửi Telegram:", e)

def get_news_sentiment(symbol):
    try:
        stock = Vnstock().stock(symbol=symbol, source="VCI")
        df_news = stock.company.news()
        if df_news is None or df_news.empty:
            return "Trung lập", "Không có tin tức mới nổi bật"
        latest_title = df_news['title'].iloc[0]
        
        negative_words = ['lỗ', 'giảm', 'phạt', 'cảnh báo', 'chậm', 'hủy', 'thanh tra', 'đình chỉ', 'xấu', 'vướng mắc']
        positive_words = ['lãi', 'tăng trưởng', 'vượt', 'ký kết', 'đạt', 'doanh thu', 'xuất khẩu', 'lợi nhuận', 'trúng thầu']
        
        score = 0
        for word in negative_words:
            if word in latest_title.lower(): score -= 1
        for word in positive_words:
            if word in latest_title.lower(): score += 1
                
        if score < 0: return "Tin xấu", latest_title
        elif score > 0: return "Tin tốt", latest_title
        return "Trung lập", latest_title
    except:
        return "Trung lập", "Không có tin tức mới nổi bật"

def analyze_multi_timeframe(df):
    df_daily = df.sort_index(ascending=True).copy()
    df_daily['time'] = pd.to_datetime(df_daily['time'])
    df_daily.set_index('time', inplace=True)
    
    # Khung tuần (1W)
    df_weekly = df_daily['close'].resample('W').last().to_frame()
    df_weekly['ema20'] = ta.trend.EMAIndicator(close=df_weekly['close'], window=20).ema_indicator()
    trend_1w = "Uptrend" if len(df_weekly) >= 2 and df_weekly['close'].iloc[-1] > df_weekly['ema20'].iloc[-1] else "Downtrend"

    # Khung ngày (1D)
    close_d = pd.to_numeric(df_daily["close"])
    rsi_series = ta.momentum.RSIIndicator(close=close_d, window=14).rsi()
    stoch_rsi_obj = ta.momentum.StochasticRSIIndicator(close=close_d, window=14, smooth1=3, smooth2=3)
    stoch_k = stoch_rsi_obj.stochrsi_k() * 100
    stoch_d_val = stoch_rsi_obj.stochrsi_d() * 100
    
    # Giả lập Banker
    rsi_mcdx = ta.momentum.RSIIndicator(close=close_d, window=20).rsi()
    banker_series = np.clip(np.where(rsi_mcdx > 50, (rsi_mcdx - 50) * 2, 0), 0, 100)
    
    latest_price = round(close_d.iloc[-1], 2)
    latest_rsi = round(rsi_series.iloc[-1], 2)
    latest_k = round(stoch_k.iloc[-1], 2)
    latest_d = round(stoch_d_val.iloc[-1], 2)
    latest_banker = round(banker_series[-1], 2)
    
    status_1d = "Quá
