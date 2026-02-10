from openai import OpenAI, AsyncOpenAI
import tiktoken # pip install tiktoken
import re
import os
import time
from dotenv import load_dotenv

load_dotenv()



def clean_text(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        book_text = file.read()

    cleaned_text = re.sub(r'\n+', ' ', book_text) # 줄바꿈을 빈칸으로 변경
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text) # 여러 빈칸을 하나의 빈칸으로

    print("cleaned_" + filename, len(cleaned_text), "characters") # 글자 수 출력

    with open("cleaned_" + filename, 'w', encoding='utf-8') as file:
        file.write(cleaned_text)

# filenames_list = ["input123.txt"]

# for filename in filenames_list:
#     clean_text(filename)



tokenizer = tiktoken.get_encoding("gpt2")

# OpenAI API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def summarize_text(text):
    """
        텍스트를 요약하는 함수
    """
    response = await client.chat.completions.create(
        model="gpt-4o-mini",  # 최신 GPT 모델 사용 가능
        messages=[ 
            {"role": "system", "content": """[명령어]
주어진 뉴스 기사 데이터를 다음 형식으로 요약해라:

[형식 규정]
- 각 항목은 • 기호로 시작
- 핵심 키워드를 <b></b> 안에 강조 표시
- 관련 수치 데이터는 <u></u> 로 강조 표시
- 출처 링크는 줄바꿈 후 URL 형식으로 표기
- 출처 링크는 뉴스기사 주소가 있을경우 먼저 표시하고 없으면 표시하지않음 https://t.me 로 시작하는 주소는 항상 표기
- 불필요한 설명 배제, 오직 팩트만 기술
- 해당사항이 없으면 표시하지않음
- 중복 내용은 한번만 표시
             
[예시]
• 이재용을 제치고 MBK 회장 김병주가 <b>13조원</b>의 개인 재산을 기록하며 <u>‘포브스 한국 자산가 1위’</u>로 등극함.  
https://n.news.naver.com/mnews/article/082/0001314933  
https://t.me/guroguru/14727  

• 분양가 산정 등을 위해 제한적인 공급이 유지되므로 고급주택의 투자 가치는 지속적으로 유지될 전망.  
https://news.einfomax.co.kr/news/articleView.html?idxno=4345866  
https://t.me/guroguru/14726  
             
• 중국 정부는 AI 및 첨단 산업에 대한 지원을 발표하여 산업 발전을 촉진하고 있음.
https://t.me/mk81_koreainvestment/18783

"""}, # "Summarize the entire content in bullet point format and display in chronological order. Must be written in Korean. Show links after each summary. Show duplicate content only once. Skip content if there is only a link and no content. Must follow the given answer format. Show only one link if given. Show all links if given more than one. Answer format: • Summary content\nhttps://\nhttps://\n\n repeat"}, # "불릿포인트 형식으로 전체 내용을 요약하고 시간순으로 표시. 각 요약내용 뒤에 링크를 표시. 중복된 내용은 한번만 표시. 링크만 있고 내용이 없다면 해당내용은 건너뜀. 제시된 답변형식을 반드시 따를것. 주어진 링크가 하나라면 하나만 표시. 주어진 링크가 두개 이상이면 모두 표시. 답변 형식:• 요약내용\nhttps://\nhttps://\n\n• 요약내용\nhttps://\n\n"},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

async def read_and_summarize(file_path:str = None, text:str = None):
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

    tokens = tokenizer.encode(text)
    print("글자수:", len(text), "토큰수", len(tokens))

    r = await summarize_text(text)

    return r

    # # OpenAI의 한 번 요청 최대 토큰 제한이 있기 때문에 텍스트를 나누어 처리할 수도 있음
    # if len(text) > 4000:  # 적절한 길이 조정 필요 (모델에 따라 다름)
    #     chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    #     summary = "\n".join([summarize_text(chunk) for chunk in chunks])
    # else:
    #     summary = summarize_text(text)

    # return summary



def run(text:str = None):
    # 실행
    # 요청 전 텍스트를 정제하고, 요약 결과를 출력

    # 요청한 원본 텍스트를 저장
    with open(f"original/origin_input{str(int(time.time()))}.txt", "w", encoding="utf-8") as input_file:
        input_file.write(text)

    if text:
        summary_result = read_and_summarize(text=text)
    else:
        file_path = "cleaned_input123.txt"  # 요약할 텍스트 파일 경로 입력
        summary_result = read_and_summarize(file_path=file_path)

    # 결과 출력
    print(summary_result)

    # 결과를 새로운 파일로 저장
    with open(f"result/output{str(int(time.time()))}.txt", "w", encoding="utf-8") as output_file:
        output_file.write(summary_result)

    return summary_result