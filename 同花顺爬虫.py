import requests
import re
import csv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def timestamp_to_beijing(ts):
    """将 Unix 时间戳转换为北京时间的字符串表示。"""
    utc_time = datetime.utcfromtimestamp(ts)
    beijing_time = utc_time + timedelta(hours=8)
    return beijing_time.strftime('%Y-%m-%d %H:%M:%S')

#同花顺财经要闻
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0'
}

url = 'https://dq.10jqka.com.cn/fuyao/hxcmp_content_stream/content_stream/v1/content_stream/api/stream_item/v1/query_for_client?stream_ids=133'

response = requests.get(url=url, headers=headers)

json_data = response.json()

r=[]
for i in json_data['data']['list']:
    t = timestamp_to_beijing(i['ctime'])
    stock_information = ""
    for j in i['stock_infos']:
        stock_information += f"股票代码: {j['code']}-股票名: {j['name']} "
    r.append(f"{t} {i['title']} [{stock_information}]:{i['summary']}")

with open("同花顺财经要闻.csv", mode="w", encoding="utf-8-sig", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["新闻内容"])
    for line in r:
        writer.writerow([line])

# r=[]
# #同花顺投资机会
# url = "https://www.10jqka.com.cn/"
#
# response = requests.get(url, headers=headers)
# response.encoding = response.apparent_encoding  # 自动识别编码
# soup = BeautifulSoup(response.text, 'html.parser')
#
# first_ul = soup.select_one('ul.content.newhe')
#
# if first_ul:
#     for i in first_ul.get_text(strip=True, separator="\n"):
#         r.append(f"投资机会模块的新闻标题为{i}")
# else:
#     print("未找到匹配的元素")
#
#
# ul_list = soup.select('ul.last')
#
# if len(ul_list) >= 2:
#     second_ul = ul_list[1]
#     for i in second_ul.get_text(strip=True, separator="\n"):
#         r.append(f"投资机会模块的新闻标题为{i}")
# else:
#     print("未找到匹配的元素")
#
# #同花顺最上面新闻
# div_list = soup.select('div.item_txt')
#
# for i in range(len(div_list)):
#     div = div_list[i]
#     for i in div.get_text(strip=True, separator="\n\n"):
#         r.append(f"重点新闻模块的新闻标题为{i}")