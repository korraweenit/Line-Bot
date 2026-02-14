import os
import requests
import json
import yfinance as yf
from datetime import datetime
import pytz # ใช้แปลงเวลาเป็นไทย

# --- 🔒 ดึงกุญแจจากตู้เซฟของ GitHub (ไม่ต้องกรอกเองแล้ว) ---
LINE_ACCESS_TOKEN = os.environ["LINE_ACCESS_TOKEN"]
MY_USER_ID = os.environ["MY_USER_ID"]

# --- ฟังก์ชันส่งไลน์ ---
def send_line_message(msg):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
    }
    data = {
        'to': MY_USER_ID,
        'messages': [{'type': 'text', 'text': msg}]
    }
    requests.post(url, headers=headers, data=json.dumps(data))

# --- ฟังก์ชันเช็คหุ้น ---
def check_market():
    symbols = ['BTC-USD', 'TSLA', 'GOOGL']
    
    # ตั้งเวลาไทย
    tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(tz)
    
    msg = f"🌅 อรุณสวัสดิ์ครับหมอ! ({now.strftime('%H:%M')})\n"
    msg += "สรุปตลาดเช้านี้:\n"
    msg += "-" * 20 + "\n"
    
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            price = ticker.fast_info.last_price
            msg += f"📈 {sym}: ${price:,.2f}\n"
        except:
            msg += f"❌ {sym}: Error\n"
            
    msg += "-" * 20
    return msg

# --- รันเลย ---
if __name__ == "__main__":
    print("Bot starting...")
    report = check_market()
    send_line_message(report)
    print("Done!")