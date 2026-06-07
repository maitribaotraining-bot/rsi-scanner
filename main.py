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
    
    # Tự tính toán Hệ thống dòng tiền giả lập Banker
    gain_20 = (delta.where(delta > 0, 0)).rolling(window=20).mean()
    loss_20 = (-delta.where(delta < 0, 0)).rolling(window=20).mean()
    rsi_20 = 100 - (100 / (1 + (gain_20 / loss_20)))
    banker_series = np.clip(np.where(rsi_20 > 50, (rsi_20 - 50) * 2, 0), 0, 100)
    
    latest_price = round(close_d.iloc[-1], 2)
    latest_rsi = round(rsi_series.iloc[-1], 2) if not np.isnan(rsi_series.iloc[-1]) else 50.0
    latest_k = round(stoch_k.iloc[-1], 2) if not np.isnan(stoch_k.iloc[-1]) else 50.0
    latest_banker = round(banker_series.iloc[-1], 2) if not np.isnan(banker_series.iloc[-1]) else 0.0
    
    # Thuật toán tính xác suất mô phỏng chuẩn xác
    match_count, success_count = 0, 0
    for i in range(50, len(df_daily) - 5):
        if abs(rsi_series.iloc[i] - latest_rsi) < 5 and abs(banker_series.iloc[i] - latest_banker) < 10:
            match_count += 1
            if (close_d.iloc[i+5] - close_d.iloc[i]) / close_d.iloc[i] > 0.02: 
                success_count += 1
                
    sim_prob = round((success_count / match_count) * 100, 1) if match_count > 0 else 50.0
    return latest_price, trend_1w, latest_rsi, latest_k, latest_banker, sim_prob

if __name__ == '__main__':
    total_symbols = len(hose_symbols)
    start_idx = 0
    group_number = 1
    total_groups = (total_symbols + BATCH_SIZE - 1) // BATCH_SIZE

    print("🚀 BẮT ĐẦU CHẠY BOT QUÉT ĐỘC LẬP CHUẨN XÁC...")

    list_day_hoang_loan = []
    list_ca_map_de_gom = []
    list_sieu_co_vao_song = []

    while start_idx < total_symbols:
        end_idx = min(start_idx + BATCH_SIZE, total_symbols)
        batch_symbols = hose_symbols[start_idx:end_idx]
        
        print(f"⏳ Đang xử lý im lặng cụm {group_number}/{total_groups}...")
        
        for symbol in batch_symbols:
            try:
                df = fetch_data_fallback(symbol)
                if df is None or len(df) < 100: 
                    continue
                
                price, trend_1w, rsi, stoch_k, banker, sim_prob = analyze_multi_timeframe(df)
                
                if rsi < 30 or stoch_k < 15:
                    list_day_hoang_loan.append(f"* **{symbol}** (Giá {price} | RSI: {rsi} | Xác suất tăng: {sim_prob}%)")
                
                elif (30 <= rsi <= 45) and banker > 20:
                    list_ca_map_de_gom.append(f"* **{symbol}** (Giá {price} | Banker: {banker}% | Xác suất tăng: {sim_prob}%)")
                
                elif trend_1w == "Uptrend" and banker > 40:
                    list_sieu_co_vao_song.append(f"* **{symbol}** (Giá {price} | Banker: {banker}% | Xác suất tăng: {sim_prob}%)")
                
                time.sleep(3)
                
            except Exception as e:
                print(f"⚠️ Bỏ qua {symbol}: {e}")
                time.sleep(3)

        start_idx += BATCH_SIZE
        group_number += 1

        if start_idx < total_symbols:
            time.sleep(DELAY_BETWEEN_BATCHES)

    if list_day_hoang_loan or list_ca_map_de_gom or list_sieu_co_vao_song:
        current_date = datetime.now().strftime("%d/%m/%Y")
        msg_final = f"🏁 *KẾT QUẢ QUÉT 200 MÃ CP (Phiên ngày {current_date})*\n"
        
        if list_day_hoang_loan:
            msg_final += f"\n🚨 *ĐÁY HOẢNG LOẠN (Ăn hồi T+)*\n" + "\n".join(list_day_hoang_loan) + "\n"
            
        if list_ca_map_de_gom:
            msg_final += f"\n🟪 *CÁ MẬP ĐÈ GOM (Trung hạn)*\n" + "\n".join(list_ca_map_de_gom) + "\n"
            
        if list_sieu_co_vao_song:
            msg_final += f"\n🔥 *SIÊU CỔ VÀO SÓNG (Đua lệnh)*\n" + "\n".join(list_sieu_co_vao_song) + "\n"
            
        msg_final += f"\n_Các mã không nằm trong danh sách trên đều đang ở trạng thái bình thường._"
        
        send_telegram(msg_final)
        print("✅ Đã hoàn thành và gửi báo cáo tổng hợp về Telegram.")
    else:
        print("💤 Hoàn thành quét. Không có cổ phiếu nào đạt điều kiện kỹ thuật hôm nay.")
