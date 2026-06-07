import pandas as pd
import requests

def check_szc_now():
    symbol = "SZC"
    headers = {"User-Agent": "Mozilla/5.0"}
    # Tải dữ liệu riêng mã SZC
    url = f"https://apipubcks.tcbs.com.vn/api/v1/stock/bars-long-term?ticker={symbol}&type=stock&resolution=D&from=1672531200&to=1798675200"
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json().get('data', [])
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['tradingDate'])
            df.set_index('date', inplace=True)
            
            # Tính RSI 14
            close_d = pd.to_numeric(df["close"])
            delta = close_d.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # Tính StochK 14
            rsi_min = rsi.rolling(window=14).min()
            rsi_max = rsi.rolling(window=14).max()
            stoch_rsi = (rsi - rsi_min) / (rsi_max - rsi_min)
            stoch_k = stoch_rsi.rolling(window=3).mean() * 100
            
            latest_rsi = round(rsi.iloc[-1], 2)
            latest_k = round(stoch_k.iloc[-1], 2)
            latest_price = df["close"].iloc[-1]
            
            print(f"==================================================")
            print(f"🔎 KẾT QUẢ CHECK RIÊNG MÃ SZC:")
            print(f"💰 Giá đóng cửa: {latest_price}")
            print(f"📊 RSI (14 ngày): {latest_rsi}")
            print(f"📉 StochK (14 ngày): {latest_k}")
            print(f"==================================================")
        else:
            print("❌ Không tải được dữ liệu từ TCBS!")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == '__main__':
    check_szc_now()
