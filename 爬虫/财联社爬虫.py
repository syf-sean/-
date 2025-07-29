import requests
import csv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def timestamp_to_beijing(ts):
    """将 Unix 时间戳转换为北京时间的字符串表示。"""
    utc_time = datetime.utcfromtimestamp(ts)
    beijing_time = utc_time + timedelta(hours=8)
    return beijing_time.strftime('%Y-%m-%d %H:%M:%S')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0'
}

#当日新闻
url = 'https://www.cls.cn/v3/depth/home/assembled/1000?app=CailianpressWeb&os=web&sv=8.4.6&sign=9f8797a1f4de66c2370f7a03990d2737'
response = requests.get(url=url, headers=headers)
json_data = response.json()

r = []
for i in json_data['data']['depth_list']:
    t = timestamp_to_beijing(i['ctime'])
    content = f"{i['title']} {t}: {i['brief']}"
    content = content.replace('\n', ' ').replace('\r', ' ').strip()
    r.append(content)

for i in json_data['data']['top_article']:
    t = timestamp_to_beijing(i['ctime'])
    temp = f"{i['title']} {t}: {i['brief']}"
    if i['article_rec']:
        for j in i['article_rec']:
            tj = timestamp_to_beijing(j['ctime'])
            temp += f" 引申的相关报道如下 {j['name']} {tj}: {j['brief']}"
    temp = temp.replace('\n', ' ').replace('\r', ' ').strip()
    r.append(temp)

with open("财联社新闻.csv", mode="w", encoding="utf-8-sig", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["新闻内容"])
    for line in r:
        writer.writerow([line])

print("已保存到 '财联社新闻.csv'")

r = []
#今日及未来消息
url = "https://www.cls.cn/"
response = requests.get(url, headers=headers)
response.encoding = response.apparent_encoding
soup = BeautifulSoup(response.text, 'html.parser')

calendar_div = soup.select_one('div.o-h.home-invest-kalendar-item')
if calendar_div:
    for _ in range(16): 
        raw_text = calendar_div.get_text(strip=True, separator="\n")
        lines = [line for line in raw_text.splitlines() if '事件' not in line and '数据' not in line and line.strip()]
        if len(lines) >= 2:
            date = lines[0]
            weekday = lines[1]
            news_items = lines[2:]
            news_formatted = " ".join([f"{chr(9312 + i)} {news}" for i, news in enumerate(news_items)])
            full_line = f"{date} {weekday} {news_formatted}"
            r.append(full_line)

        calendar_div = calendar_div.find_next_sibling()
        if not calendar_div:
            break
else:
    print("未找到投资日历部分")



with open("财联社投资日历.csv", mode="w", encoding="utf-8-sig", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["新闻内容"])
    for line in r:
        writer.writerow([line])

print("已保存到 '财联社投资日历.csv'")
