import re


with open("result/output1741397746.txt", "r", encoding="utf-8") as f:
    data = f.read()


def split_telegram_messages(data, max_length=4096) -> list:
    result = []
    channel_pattern = re.compile(r'(\d+\.\s*<a href=[^>]+>.*?</a>\s*)(.*?)(?=\d+\.\s*<a href=|\Z)', re.DOTALL)
    for match in channel_pattern.finditer(data):
        header = match.group(1).strip()
        content = match.group(2).strip()

        result.append(header + "\n\n" + content)
        continue
    return result











split_telegram_messages(data=data)