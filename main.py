# Cần cài đặt thư viện trước trong GitHub Actions bằng cách thêm: pip install vnstock3
from vnstock3 import Vnstock
import time

def check_stock_data():
    symbols = ["SZC", "HPG", "SSI"] # Anh điền danh sách 200 mã vào đây
    print("🚀 Bắt đầu quét dữ liệu qua vnstock...")
    
    for symbol in symbols:
        try:
            # Khởi tạo đối tượng vnstock
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            # Lấy dữ liệu lịch sử
            df = stock.quote.history(start='2026-01-01', end='2026-06-07')
            
            if not df.empty:
                print(f"✅ Đã quét xong mã: {symbol} | Giá cuối: {df['close'].iloc[-1]}")
            else:
                print(f"⚠️ Mã {symbol} không có dữ liệu.")
                
        except Exception as e:
            print(f"❌ Lỗi khi quét {symbol}: {e}")
        
        time.sleep(1) # Nghỉ để tránh bị khóa IP

if __name__ == '__main__':
    check_stock_data()
