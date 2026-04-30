#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from datetime import datetime
import time

# 設定
BOT_TOKEN = "8238666602:AAFemnNm015QQVLi4Py0eayHEJCNZrNPRv0"
CHAT_ID = "1848403541"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})
        print(f"發送訊息: {response.status_code}")
        return response.json()
    except Exception as e:
        print(f"發送失敗: {e}")
        return None

def get_exhibitions():
    exhibitions = []
    
    try:
        print("正在從文化部 API 獲取資料...")
        url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=6"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        print(f"API 回應狀態: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"獲得 {len(data)} 筆資料")
            
            for item in data[:30]:
                try:
                    end_date_str = item.get("endDate", "")
                    if end_date_str:
                        try:
                            end_date = datetime.strptime(end_date_str, "%Y/%m/%d")
                            if end_date < datetime.now():
                                continue
                        except:
                            pass
                    
                    location = item.get("location", "未提供")
                    title = item.get("title", "未提供")
                    
                    # 取得展覽介紹
                    description = item.get("descriptionFilterHtml", "")
                    if not description:
                        description = item.get("intro", "暫無介紹")
                    
                    # 清理 HTML 標籤
                    if description:
                        description = description.replace("<br>", "\n")
                        description = description.replace("<br/>", "\n")
                        description = description.replace("<p>", "")
                        description = description.replace("</p>", "\n")
                        # 限制介紹長度
                        if len(description) > 200:
                            description = description[:200] + "..."
                    
                    showInfo = item.get("showInfo", [])
                    if showInfo and len(showInfo) > 0:
                        show_time = showInfo[0].get("time", "請洽主辦單位")
                        location_name = showInfo[0].get("locationName", "未提供")
                        # 取得展覽地址
                        address = showInfo[0].get("location", "未提供")
                    else:
                        show_time = "請洽主辦單位"
                        location_name = "未提供"
                        address = "未提供"
                    
                    start_date = item.get("startDate", "")
                    end_date = item.get("endDate", "")
                    
                    if start_date and end_date:
                        date_range = f"{start_date} ~ {end_date}"
                    else:
                        date_range = "請洽主辦單位"
                    
                    exhibitions.append({
                        "縣市": location,
                        "名稱": title,
                        "時間": show_time,
                        "日期": date_range,
                        "地點": location_name,
                        "地址": address,
                        "介紹": description if description else "暫無介紹"
                    })
                    
                except Exception as e:
                    print(f"解析展覽資料錯誤: {e}")
                    continue
                    
    except Exception as e:
        print(f"獲取文化部資料失敗: {e}")
    
    return exhibitions

def main():
    print("=" * 50)
    print("🤖 台灣展覽通報機器人啟動")
    print(f"⏰ 執行時間: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
    print("=" * 50)
    
    send_message("🤖 展覽通報機器人開始搜尋...")
    time.sleep(1)
    
    exhibitions = get_exhibitions()
    print(f"\n✅ 總共找到 {len(exhibitions)} 個展覽")
    
    if not exhibitions:
        send_message("😢 本週沒有找到展覽資訊")
        return
    
    by_region = {}
    for ex in exhibitions:
        region = ex['縣市']
        if region not in by_region:
            by_region[region] = []
        by_region[region].append(ex)
    
    message = f"📅 <b>台灣展覽週報</b>\n"
    message += f"🗓 更新時間：{datetime.now().strftime('%Y/%m/%d %H:%M')}\n"
    message += f"📊 共找到 {len(exhibitions)} 個展覽\n"
    message += "=" * 30 + "\n\n"
    
    count = 0
    for region in sorted(by_region.keys()):
        exs = by_region[region]
        message += f"📍 <b>{region}</b>\n\n"
        
        for ex in exs[:5]:
            count += 1
            if count > 15:
                break
                
            message += f"🎨 <b>展覽名稱：{ex['名稱']}</b>\n"
            message += f"🕐 展覽時間：{ex['時間']}\n"
            message += f"📅 展覽日期：{ex['日期']}\n"
            message += f"📌 展覽地點：{ex['地點']}\n"
            message += f"📍 展覽地址：{ex['地址']}\n"
            message += f"📖 展覽介紹：{ex['介紹']}\n"
            message += "\n" + "-" * 30 + "\n\n"
        
        if count > 15:
            break
    
    max_length = 4000
    if len(message) > max_length:
        chunks = []
        current = ""
        for line in message.split("\n"):
            if len(current) + len(line) + 1 > max_length:
                chunks.append(current)
                current = line + "\n"
            else:
                current += line + "\n"
        if current:
            chunks.append(current)
        
        print(f"訊息過長，分成 {len(chunks)} 段發送")
        for i, chunk in enumerate(chunks, 1):
            print(f"發送第 {i}/{len(chunks)} 段...")
            send_message(chunk)
            time.sleep(2)
    else:
        send_message(message)
    
    print("\n✅ 執行完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
