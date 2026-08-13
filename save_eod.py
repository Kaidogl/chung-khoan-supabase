from datetime import datetime
from vnstock3 import Vnstock
from supabase import create_client, Client

# 1. Thông tin kết nối dự án Supabase của bạn
SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "sb_publishable_wvr_Eky8uuVTjJ02YqiISw_1yKHQU9V"

# Khởi tạo Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_and_save_eod():
    print("🚀 Bắt đầu tiến trình lấy dữ liệu kết phiên...")
    
    # 2. Định dạng ngày hôm nay (YYYY-MM-DD)
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Danh sách các mã cổ phiếu bạn theo dõi
    danh_sach_ma = ["HPG", "SSI", "VND", "VNM", "VCB", "FPT", "MWG"] 
    
    # Khởi tạo thư viện Vnstock
    stock = Vnstock()
    data_to_insert = []
    
    for ticker in danh_sach_ma:
        try:
            # Gọi API lấy dữ liệu lịch sử ngày hôm nay
            df = stock.stock(symbol=ticker, source='tcbs').quote.history(start=today_str, end=today_str)
            
            if df is None or df.empty:
                print(f"⚠️ Không có dữ liệu mới cho mã {ticker} ngày {today_str}.")
                continue
                
            row = df.iloc[0] # Lấy dòng dữ liệu đầu tiên
            
            # Khớp cấu trúc dữ liệu với các trường trong bảng Supabase của bạn
            record = {
                "ticker": ticker,
                "trading_date": today_str,
                "open_price": float(row['open']),
                "high_price": float(row['high']),
                "low_price": float(row['low']),
                "close_price": float(row['close']),
                "volume": int(row['volume'])
            }
            data_to_insert.append(record)
            print(f"✅ Đã xử lý dữ liệu: {ticker}")
            
        except Exception as e:
            print(f"🚨 Lỗi khi lấy dữ liệu mã {ticker}: {e}")

    # 3. Đẩy dữ liệu vào bảng 'lich_su_gia' trên Supabase
    if data_to_insert:
        try:
            supabase.table("lich_su_gia").upsert(data_to_insert).execute()
            print(f"\n🎉 THÀNH CÔNG: Đã lưu {len(data_to_insert)} mã vào cơ sở dữ liệu Supabase của bạn!")
        except Exception as e:
            print(f"🚨 Lỗi khi kết nối hoặc ghi vào Supabase: {e}")
    else:
        print("\n❌ Kết thúc: Không có dữ liệu nào được lưu.")

# Kích hoạt chạy hàm
get_and_save_eod()

