import os
import requests
import json
import yfinance as yf
from datetime import datetime
import pytz
import google.generativeai as genai

# --- 🔒 ดึงกุญแจจากตู้เซฟ ---
LINE_ACCESS_TOKEN = os.environ["LINE_ACCESS_TOKEN"]
MY_USER_ID = os.environ["MY_USER_ID"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# --- ตั้งค่า Gemini AI ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash') # ใช้รุ่น Flash เพราะเร็วและเพียงพอสำหรับงานสรุป

def get_ai_news():
    prompt = """
    สรุปข่าวเด่นรายวันด้าน Crypto และเศรษฐกิจมหภาค (Macroeconomics) สั้นๆ กระชับ
    เน้นประเด็นสำคัญที่มีผลต่อตลาด (เช่น ข่าวระดับโลก, นโยบายภาษี/ดอกเบี้ย, หรือ Sentiment นักลงทุน)
    และวิเคราะห์ปัจจัยเร่ง (Catalysts) สั้นๆ
    ความยาวไม่เกิน 5-7 บรรทัด เขียนให้อ่านง่ายเหมาะกับอ่านผ่านแอป LINE
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ AI ไม่สามารถสรุปข่าวได้: {str(e)}"

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

def check_market_and_news():
    # เพิ่ม VOO และ QQQ เข้ามาในพอร์ต
    symbols = ['BTC-USD', 'MSFT', 'GOOGL', 'VOO', 'FXI','VXUS']
    
    tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(tz)
    
    msg = f"พักเที่ยงแล้วครับหมอ! 📊 อัปเดตตลาด ({now.strftime('%H:%M')})\n"
    msg += "-" * 20 + "\n"
    
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            price = ticker.fast_info.last_price
            msg += f"📈 {sym}: ${price:,.2f}\n"
        except:
            msg += f"❌ {sym}: Error\n"
            
    msg += "-" * 20 + "\n"
    msg += "📰 🤖 AI Macro & Crypto News:\n"
    msg += get_ai_news()
    
    return msg

if __name__ == "__main__":
    print("Bot starting...")
    report = check_market_and_news()
    send_line_message(report)
    print("Done!")