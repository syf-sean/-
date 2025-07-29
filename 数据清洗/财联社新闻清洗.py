from openai import OpenAI
import csv
import ast

client = OpenAI(
    api_key="48d27087-6f8d-473a-b37a-f9b349f94d81",
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    timeout=1800,
)


prompt_template = (
    "我将以列表形式提供来自财联社的新闻，格式如下：\n"
    "*[新闻标题 发布时间：新闻摘要（可选）引申的相关报道如下（如有）：... , 新闻标题 发布时间：新闻摘要]*\n\n"
    "你的任务如下：\n"
    "1. 对每条新闻判断是否对 A 股市场具有实质性影响，符合以下任一条件即可保留：\n"
    "   - 明确提及 **A 股上市公司**（仅限在上海或深圳证券交易所挂牌的企业）；\n"
    "   - 涉及 A 股相关板块（如人工智能、新能源、医药、券商、军工、芯片、机器人等）可能存在短期或长期投资机会；\n"
    "   - 涉及对 A 股整体走势可能造成影响的宏观经济、财政/货币政策、监管政策或地缘政治事件；\n"
    "   - 为具有行业号召力的会议、展会、科技竞赛、技术发布等，可能催化板块行情（即使未提及具体公司）。\n\n"
    "2. 若新闻符合以下任一情形，请直接删除（不保留）：\n"
    "   - 未在 A 股上市的公司（如华为（未上市）、特斯拉（美股）、腾讯（港股）、台积电（台股）等）；\n"
    "   - 属于与 A 股市场无关的国际动态或企业资讯；\n"
    "   - 内容空泛、缺乏投资价值或无明确实质信息（如例行会议、泛泛宣传、机构调研无具体成果等）。\n\n"
    "3. 对保留的新闻，请进行以下处理：\n"
    "   - 将标题与摘要融合、精炼，只保留关键信息；\n"
    "   - 明确指出相关行业板块（如“或带动机器人概念股”）；\n"
    "   - 保留原始 **发布时间格式**，仅替换为精简后的新闻内容。\n\n"
    "**请严格按照以下格式输出（不要添加额外解释，输出符号需均为英文）**：\n"
    "[发布时间：新闻内容, 发布时间：新闻内容]\n"
    "财联社新闻如下：\n{news}"
)


with open("财联社新闻.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = [row[0] for row in reader if row]

all_cleaned_news = []  # 用于收集所有循环中生成的新闻内容

for i in range(1, 30, 10):
    prompt = prompt_template.format(news=rows[i:i + 10])

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
        print(f"处理第 {i} ~ {i + 10} 条新闻时出错：", e)


try:
    with open("财联社新闻clean.csv", mode="w", encoding="utf-8-sig", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["新闻内容"])
        for line in all_cleaned_news:
            writer.writerow([line])
except Exception as e:
    print("写入 CSV 文件时出错：", e)
