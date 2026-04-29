#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from datetime import datetime

# 設定
BOT_TOKEN = "8238666602:AAFemnNm015QQVLi4Py0eayHEJCNZrNPRv0"
CHAT_ID = "1848403541"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

def get_exhibitions():
    exhibitions = []
    try:
        url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=6"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            for item in data[:20]:  # 取前20筆
                try:
                    location = item.get("location", "未提供")
                    title = item.get("title", "未提供")
                    
                    showInfo = item.get("showInfo", [])
                    show_time = showInfo[0].get("time", "未提供") if showInfo else "未提供"
                    location_name = showInfo[0].get("locationName", "未提供") if showInfo else "未提供"
                    
                    start_date = item.get("startDate", "")
                    end_date = item.get("endDate", "")
                    
                    exhibitions.append({
                        "地區": location,
                        "名稱": title,
                        "時間": show_time,
                        "日期": f"{start_date} ~ {end_date}",
                        "地點": location_name
                    })
                except:
                    continue
    except Exception as e:
        print(f"錯誤: {e}")
    
    return exhibitions

def main():
    send_message("🤖 展覽通報機器人開始搜尋...")
    
    exhibitions = get_exhibitions()
    
    if not exhibitions:
        send_message("本週沒有找到展覽資訊 😢")
        return
    
    message = f"📅 <b>台灣展覽週報</b>\n"
    message += f"🗓 {datetime.now().strftime('%Y/%m/%d %H:%M')}\n"
    message += f"📊 共 {len(exhibitions)} 個展覽\n"
    message += "=" * 30 + "\n\n"
    
    for i, ex in enumerate(exhibitions[:15], 1):  # 顯示前15個
        message += f"{i}. 🎨 <b>{ex['名稱']}</b>\n"
        message += f"   📍 {ex['地區']} - {ex['地點']}\n"
        message += f"   📅 {ex['日期']}\n"
        message += f"   🕐 {ex['時間']}\n\n"
    
    # 分段發送(避免訊息太長)
    chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
    for chunk in chunks:
        send_message(chunk)
    
    print("✅ 完成!")

if __name__ == "__main__":
    main()
