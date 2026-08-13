from datetime import datetime
from vnstock3 import Vnstock
from supabase import create_client, Client

# 1. Thông tin kết nối Supabase của bạn
SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "sb_publishable_wvr_Eky8uuVTjJ02YqiISw_1yKHQU9V"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_and_save_eod():
    print("🚀 Bắt đầu lấy toàn bộ danh sách mã cổ phiếu trên thị trường...")
    stock = Vnstock()
    
    # 🔥 THAY ĐỔI CỐT LÕI: Tự động tải danh sách hơn 1600 mã từ HOSE, HNX, UPCoM
    df_symbols = stock.all_symbols()
    danh_sach_ma = df_symbols['ticker'].tolist()
    print(f"📊 Tìm thấy tổng cộng {len(danh_sach_ma)} mã chứng khoán.")
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    data_to_insert = []
    
    # Duyệt qua từng mã để lấy dữ liệu nến ngày
    for i, ticker in enumerate(danh_sach_ma):
        try:
            df = stock.stock(symbol=ticker, source='tcbs').quote.history(start=today_str, end=today_str)
            
            if df is None or df.empty:
                continue
                
            row = df.iloc[0]
            
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
            
            # In tiến độ ra màn hình log cứ sau mỗi 100 mã
            if (i + 1) % 100 == 0:
                print(f"🔄 Đã xử lý {i + 1}/{len(danh_sach_ma)} mã...")
            
        except Exception:
            # Bỏ qua các mã lỗi (ví dụ mã bị hủy niêm yết, ngừng giao dịch) để script chạy tiếp
            continue

    # 3. Đẩy hàng loạt dữ liệu vào Supabase
    if data_to_insert:
        try:
            print(f"📦 Đang đẩy {len(data_to_insert)} dòng dữ liệu vào Supabase...")
            # Chia nhỏ dữ liệu gửi lên (mỗi lần 500 dòng) để tránh quá tải payload của API Supabase
            for i in range(0, len(data_to_insert), 500):
                chunk = data_to_insert[i:i + 500]
                supabase.table("lich_su_gia").upsert(chunk).execute()
            print("🎉 THÀNH CÔNG: Đã đồng bộ dữ liệu toàn thị trường!")
        except Exception as e:
            print(f"🚨 Lỗi khi ghi dữ liệu vào Supabase: {e}")
    else:
        print("❌ Không có dữ liệu nào được lưu.")

if __name__ == "__main__":
    get_and_save_eod()
