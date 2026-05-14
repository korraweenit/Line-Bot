import os
import requests
import json
import yfinance as yf
from datetime import datetime
import pytz
import google.generativeai as genai

# --- 🔒 ดึงกุญแจ ---
LINE_ACCESS_TOKEN = os.environ["LINE_ACCESS_TOKEN"]
MY_USER_ID = os.environ["MY_USER_ID"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') 

def get_ai_news(date_str):
    prompt = f"วันนี้วันที่ {date_str} สรุปข่าว Crypto & Macroeconomics สั้นๆ 5 บรรทัด พร้อมวิเคราะห์ Catalysts"
    try:
        return model.generate_content(prompt).text.strip()
    except Exception as e:
        return f"❌ AI สรุปข่าวไม่ได้: {e}"

def send_line_message(msg):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'}
    data = {'to': MY_USER_ID, 'messages': [{'type': 'text', 'text': msg}]}
    requests.post(url, headers=headers, data=json.dumps(data))

def check_market_report(now):
    symbols = ['MSFT', 'GOOGL', 'VOO', 'FXI', 'VXUS']
    msg = f"โย่ววววววว Bew! 📊 อัปเดตตลาด ({now.strftime('%H:%M')})\n" + ("-" * 20) + "\n"
    
    # ดึงราคา BTC (Coinbase API - กันเหนียวเรื่อง IP US)
    try:
        res = requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot")
        msg += f"📈 BTC-USD: ${float(res.json()['data']['amount']):,.2f}\n"
    except: msg += "❌ BTC-USD: Error\n"

    for sym in symbols:
        try:
            p = yf.Ticker(sym).fast_info.last_price
            msg += f"📈 {sym}: ${p:,.2f}\n"
        except: msg += f"❌ {sym}: Error\n"
            
    msg += ("-" * 20) + "\n📰 🤖 AI News:\n" + get_ai_news(now.strftime('%d/%m/%Y'))
    return msg

# --- 🚀 Main Logic ---
if __name__ == "__main__":
    tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(tz)
    hour = now.hour

    # ระบบตรวจสอบช่วงเวลา (Routing)
    if 11 <= hour <= 13:
        # ช่วงเที่ยง: ส่งรายงานตลาด
        report = check_market_report(now)
        send_line_message(report)
    elif 14 <= hour <= 16:
        # ช่วงบ่ายสาม: ส่ง Reminder ฝึกภาษา
        study_msg = "🔔 คุณหมอบิวครับ! อย่าลืมทำ\n- Listen & Repeat\n- Shadowing\n- Listen Academic\n\nลงทุนในตัวเองคือ High-Yield ที่สุดครับ! ✌️"
        send_line_message(study_msg)
    else:
        # กรณีรันมือ (Manual) นอกช่วงเวลา
        print("Manual run detected. Sending Full Report.")
        send_line_message(check_market_report(now))
