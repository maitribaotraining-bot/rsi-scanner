from vnstock import Vnstock
import pandas as pd
import ta
import requests
import time
import os
from datetime import datetime

# ====================================
# TELEGRAM
# ====================================
BOT_TOKEN = "8937864972:AAGOMsxZOG7s6bKVW1al93ahQcfWU3lUYUg"
CHAT_ID = "1259162767"

# ====================================
# DANH SACH 200 MA POTENTIAL (Cập nhật 2026)
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
    "MSB", "SSB", "BSI", "CTS", "ORS", "AGR", "SHS", "MBS",
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
# TỰ ĐỘNG TÍNH TOÁN BATCH (20 NHÓM TỪ 1 ĐẾN 20)
# ====================================
BATCH_SIZE = 10
total_slots = len(hose_symbols) // BATCH_SIZE  # Có 20 nhóm

current_minute = datetime.now().minute
current_hour = datetime.now().hour

total_runs_today = (current_hour * 4) + (current_minute // 15)
batch_index = total_runs_today % total_slots

# Đổi số 0 thành Nhóm 1, Nhóm 2,... cho anh dễ nhìn trên Telegram
group_number = batch_index + 1 

start_index = batch_index * BATCH_SIZE
end_index = start_index + BATCH_SIZE
batch_symbols = hose_symbols[start_index:end_index]

# ====================================
# HAM HỖ TRỢ GỬI TELEGRAM NHANH
# ====================================
def send_telegram(text_message):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text_message}
        )
    except Exception as e:
        print("Lỗi gửi Telegram:", e)

# HAM TÍNH RSI (Đã sửa lỗi đóng ngoặc ở dòng 82 cũ)
def get_rsi(df):
    df_sorted = df.sort_index(ascending=True)
    close = pd.to_numeric(df_sorted["close"])
    rsi = ta.momentum.RSIIndicator(close=close, window=14).rsi()
    return round(rsi.iloc[-1], 2)

# ====================================
# 1. THÔNG BÁO BẮT ĐẦU QUÉT NHÓM
# ====================================
print(f"--- KHỞI ĐỘNG NHÓM {group_number} ---")
send_telegram(
    f"🔍 [BOT] Bắt đầu quét NHÓM {group_number}/20\n"
    f"📋 Danh sách 10 mã: {', '.join(batch_symbols)}"
)

count_signals_found = 0

# ====================================
# 2. VÒNG LẶP QUET VÀ TRẢ KẾT QUẢ TỪNG LẦN (REAL-TIME)
# ====================================
for symbol in batch_symbols:
    try:
        print("Scanning:", symbol)
        stock = Vnstock().stock(symbol=symbol, source="VCI")
        
        df = stock.quote.history(
            start="2024-01-01",
            end="2026-12-31",
            interval="1D"
        )

        if df is None or len(df) < 20:
            continue

        latest_rsi = get_rsi(df)
        
        df_sorted = df.sort_index(ascending=True)
        latest_price = round(pd.to_numeric(df_sorted["close"]).iloc[-1], 2)

        print(symbol, "RSI:", latest_rsi)

        # THOẢ ĐIỀU KIỆN LÀ BẮN TIN NHẮN NGAY LẬP TỨC
        if latest_rsi < 30:
            count_signals_found += 1
            signal_msg = (
                f"🟢 PHÁT HIỆN TÍN HIỆU (Nhóm {group_number})\n"
                f"Mã cổ phiếu: {symbol}\n"
                f"Giá hiện tại: {latest_price}\n"
                f"Chỉ số RSI14: {latest_rsi} (< 30 - Quá bán)"
            )
            send_telegram(signal_msg)

        time.sleep(4) # Chống bị khóa API do spam lệnh nhanh

    except Exception as e:
        print(f"Lỗi tại mã {symbol}: {e}")
        time.sleep(6)

# ====================================
# 3. THÔNG BÁO KẾT THÚC NHÓM
# ====================================
print(f"--- KẾT THÚC NHÓM {group_number} ---")
send_telegram(
    f"🏁 [BOT] Đã quét xong xuôi NHÓM {group_number}/20.\n"
    f"📊 Tìm thấy: {count_signals_found} mã thỏa điều kiện."
)
