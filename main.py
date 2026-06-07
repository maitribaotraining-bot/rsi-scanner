import pandas as pd
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

BATCH_SIZE = 19
DELAY_BETWEEN_BATCHES = 120 

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

def fetch_data_fallback(symbol):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://apipubcks.tcbs.com.vn/api/v1/stock/bars-long-term?ticker={symbol}&type=stock&resolution=D&from=1672531200&to=1798675200"
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json().get('data', [])
            if data:
                df = pd.DataFrame(data)
                df = df.rename(columns={'tradingDate': 'date'})
                return df
    except:
        pass
    return None

def get_news_sentiment(symbol):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://apipubcks.tcbs.com.vn/api/v1/stock/{symbol}/news-v2?size=1"
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            news_list = res.json().get('data', [])
            if news_list:
                latest_title = news_list[0].get('title', '')
                negative_words = ['lỗ', 'giảm', 'phạt', 'cảnh báo', 'chậm', 'hủy', 'thanh tra', 'đình chỉ', 'xấu']
                positive_words = ['lãi', 'tăng trưởng', 'vượt', 'ký kết', 'đạt', 'doanh thu', 'lợi nhuận', 'trúng thầu']
                
                score = 0
                for word in negative_words:
                    if word in latest_title.lower(): score -= 1
                for word in positive_words:
                    if word in latest_title.lower(): score += 1
                        
                if score < 0: return "Tin xấu", latest_title
                elif score > 0: return "Tin tốt", latest_title
                return "Trung lập", latest_title
    except:
        pass
    return "Trung lập", "Không có tin tức mới nổi bật"

def analyze_multi_timeframe(df):
    df_daily = df.sort_values(by='date', ascending=True).copy()
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    df_daily.set_index('date', inplace=True)
            
    # Tự tính toán EMA20 Tuần
    df_weekly = df_daily['close'].resample('W').last().to_frame()
    df_weekly['ema20'] = df_weekly['close'].ewm(span=20, adjust=False).mean()
    trend_1w = "Uptrend" if len(df_weekly) >= 2 and df_weekly['close'].iloc[-1] > df_weekly['ema20'].iloc[-1] else "Downtrend"

    # Tự tính toán RSI 14 Ngày bằng toán học lõi Pandas
    close_d = pd.to_numeric(df_daily["close"])
    delta = close_d.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi_series = 100 - (100 / (1 + rs))
    
    # Tự tính toán Stochastic RSI 14 Ngày
    rsi_min = rsi_series.rolling(window=14).min()
    rsi_max = rsi_series.rolling(window=14).max()
    stoch_rsi = (rsi_series - rsi_min) / (rsi_max - rsi_min)
    stoch_k = stoch_rsi.rolling(window=3).mean() * 100
    stoch_d_val = stoch_k.rolling(window=3).mean()
    
    # Tự tính toán Hệ thống dòng tiền giả lập Banker
    gain_20 = (delta.where(delta > 0, 0)).rolling(window=20).mean()
    loss_20 = (-delta.where(delta < 0, 0)).rolling(window=20).mean()
    rsi_20 = 100 - (100 / (1 + (gain_20 / loss_20)))
    banker_series = np.clip(np.where(rsi_20 > 50, (rsi_20 - 50) * 2, 0), 0, 100)
    
    latest_price = round(close_d.iloc[-1], 2)
    latest_rsi = round(rsi_series.iloc[-1], 2) if not np.isnan(rsi_series.iloc[-1]) else 50.0
    latest_k = round(stoch_k.iloc[-1], 2) if not np.isnan(stoch_k.iloc[-1]) else 50.0
    latest_d = round(stoch_d_val.iloc[-1], 2) if not np.isnan(stoch_d_val.iloc[-1]) else 50.0
    latest_banker = round(banker_series.iloc[-1], 2) if not np.isnan(banker_series.iloc[-1]) else 0.0
    
    status_1d = "Quá bán" if latest_rsi < 30 else ("Tín hiệu đáy" if latest_k < 20 and latest_k > latest_d else "Bình thường")

    # Thuật toán tính xác suất mô phỏng chuẩn xác
    match_count, success_count = 0, 0
    for i in range(50, len(df_daily) - 5):
        if abs(rsi_series.iloc[i] - latest_rsi) < 5 and abs(banker_series.iloc[i] - latest_banker) < 10:
            match_count += 1
            if (close_d.iloc[i+5] - close_d.iloc[i]) / close_d.iloc[i] > 0.02: 
                success_count += 1
                
    sim_prob = round((success_count / match_count) * 100, 2) if match_count > 0 else 50.0
    return latest_price, trend_1w, status_1d, latest_rsi, latest_k, latest_banker, sim_prob

if __name__ == '__main__':
    total_symbols = len(hose_symbols)
    start_idx = 0
    group_number = 1

    print(f"🚀 BẮT ĐẦU CHẠY BOT QUÉT ĐỘC LẬP CHUẨN XÁC...")

    while start_idx < total_symbols:
        end_idx = min(start_idx + BATCH_SIZE, total_symbols)
        batch_symbols = hose_symbols[start_idx:end_idx]
        
        print(f"⏳ Đang quét cụm {group_number}...")
        signals_found = []
        
        for symbol in batch_symbols:
            try:
                df = fetch_data_fallback(symbol)
                if df is None or len(df) < 100: 
                    continue
                
                price, trend_1w, status_1d, rsi, stoch_k, banker, sim_prob = analyze_multi_timeframe(df)
                
                # Bộ lọc điều kiện khắt khe
                if (rsi < 30) or (stoch_k < 20 and banker > 15):
                    sentiment, news_title = get_news_sentiment(symbol)
                    
                    if trend_1w == "Uptrend" and banker > 20:
                        if sentiment == "Tin xấu":
                            verdict = "MUA GOM - Tin xấu ra để đè giá, cá mập âm thầm hấp thụ hết lực bán, cơ hội gom giá tốt."
                        else:
                            verdict = "MUA GOM - Xu hướng lớn ủng hộ, cá mập đang đẩy tiền gom hàng, xác suất nổ tím cao."
                        decision_icon = "🟪"
                    elif trend_1w == "Downtrend":
                        verdict = f"THEO DÕI - Khung tuần xấu, rủi ro dính bẫy giá tăng (Bull-trap) do tin tức {sentiment.lower()} bủa vây."
                        decision_icon = "🟡"
                    else:
                        verdict = "THEO DÕI - Cổ phiếu đang tích lũy đi ngang, chờ dòng tiền bùng nổ rõ ràng hơn."
                        decision_icon = "🟡"

                    item_str = (
                        f"\n**{symbol} -> Giá: {price}**\n"
                        f"+ 🌐 Đa khung: Tuần (1W): {trend_1w} | Ngày (1D): {status_1d}\n"
                        f"+ 📊 Kỹ thuật: RSI: {rsi} | StochK: {stoch_k} | Banker: {banker}%\n"
                        f"+ 📰 Tin tức: **{sentiment}** ({news_title[:45]}...)\n"
                        f"+ 📈 Mô phỏng: Xác suất tăng giá 5 phiên tới: {sim_prob}%\n"
                        f"+ {decision_icon} Nhận định: {verdict}\n"
                        f"---"
                    )
                    signals_found.append(item_str)
                time.sleep(3)
                
            except Exception as e:
                print(f"⚠️ Bỏ qua {symbol}: {e}")
                time.sleep(3)
                
        # CHỈ GỬI TELEGRAM KHI CÓ TÍN HIỆU (BỎ TIÊU ĐỀ THỪA)
        if len(signals_found) > 0:
            msg_summary = "".join(signals_found)
            send_telegram(msg_summary)
            print(f"✅ Đã gửi tín hiệu cụm {group_number} về Telegram.")
        else:
            print(f"💤 Cụm {group_number} không có tín hiệu.")

        start_idx += BATCH_SIZE
        group_number += 1

        if start_idx < total_symbols:
            time.sleep(DELAY_BETWEEN_BATCHES)

    print("\n🏁 HỆ THỐNG HOÀN THÀNH QUÉT TOÀN BỘ 200 MÃ!")
