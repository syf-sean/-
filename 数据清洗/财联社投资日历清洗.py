from openai import OpenAI
import csv
import ast


client = OpenAI(
    api_key=os.environ.get("DouBao_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    timeout=1800,
)


prompt_template = (
    "我将以列表形式提供涵盖五天的重要财经新闻，格式如下：\n"
    "*[2025-07-25 星期五 ① 新闻一 ② 新闻二, 2025-07-26 星期六 ① 新闻一]*\n\n"
    "你的任务如下：\n"
    "1. 判断每条新闻是否对 A 股市场产生实质性影响：\n"
    "   - 是否涉及 A 股上市公司；\n"
    "   - 是否能反映 A 股相关板块（如人工智能、新能源、医药、券商、军工、芯片、机器人等）的短期或长期投资机会；\n"
    "   - 是否涉及宏观经济、监管政策、财政/货币政策等对 A 股市场可能有广泛影响的内容；\n"
    "   - 是否为具有影响力的行业会议、科技竞赛、展会或发布活动，可能催化特定概念股热度，即使未提及具体公司。\n"
    "2. 若无明显影响，或涉及以下情况，请删除该新闻：\n"
    "   - 未在 A 股上市的公司（如华为（未上市）、特斯拉（美股）、腾讯（港股）、台积电（台股）等）；\n"
    "   - 与 A 股市场无关的境外动态；\n"
    "   - 无实际内容或无投资价值的例行通报、泛泛会议、无关宣传等。\n"
    "3. 对保留的新闻，请：\n"
    "   - 精炼、压缩内容，仅保留关键信息；\n"
    "   - 明确涉及板块（如可激活机器人概念股等）；\n"
    "   - 保留原有结构格式（如日期、星期、编号等），仅修改新闻内容。\n\n"
    "请严格按照以下格式返回结果（不要添加多余解释）：\n"
    "[2025-07-25 星期五 ① 精简后的新闻一 ② 精简后的新闻二, 2025-07-26 星期六 ① 精简后的新闻一]\n"
    "投资日历如下：\n{event}"
)

with open("财联社投资日历.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = [row[0] for row in reader if row]

all_cleaned_news = []  # 用于收集所有循环中生成的新闻内容

for i in range(0, 12, 5):
    prompt = prompt_template.format(event=rows[i:i + 5])

    try:
        response = client.chat.completions.create(
            model="doubao-seed-1-6-250615",
            messages=[
                {
                    "role": "system",
                    "content": "你是一名专业且严谨的金融舆情分析助手，专注于判断财经事件对 **中国 A 股市场** 的影响。",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            extra_body={
                "thinking": {
                    "type": "disabled",  # 不使用深度思考能力
                    # "type": "enabled", # 使用深度思考能力
                    # "type": "auto", # 模型自行判断是否使用深度思考能力
                }
            },
        )
        response = response.choices[0].message.content
        print(response)

        # 提取并格式化为 Python 列表
        quoted_str = "[" + ", ".join(f'"{item.strip()}"' for item in response.strip("[]").split(",")) + "]"
        response_list = ast.literal_eval(quoted_str)

        all_cleaned_news.extend(response_list)

    except Exception as e:
        print(f"处理第 {i} ~ {i + 5} 条新闻时出错：", e)


try:
    with open("财联社投资日历clean.csv", mode="w", encoding="utf-8-sig", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["新闻内容"])
        for line in all_cleaned_news:
            writer.writerow([line])
except Exception as e:
    print("写入 CSV 文件时出错：", e)

