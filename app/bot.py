import os
import re
import time
import json
from telethon import TelegramClient, events
from dotenv import load_dotenv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app import gpt_fetch
from app import database
from app import logger
from app import scheduler_loop

DEBUG_MODE = False

LOG = logger.makeLogger()

USER_DB = database.user_db("database/user.db", "user_table")
DB = database.subscribe_db("database/subscribe.db", "subscribe_table")

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
session_name = os.getenv("SESSION_NAME")
# phone = os.getenv("PHONE_NUMBER")

bottoken = os.getenv("TELEGRAM_BOT_TOKEN")

bot = TelegramClient('session/bot_session', api_id, api_hash).start(bot_token=bottoken)
client = TelegramClient('session/user_session', api_id, api_hash, device_model=session_name)
client.start()

# # 마지막 요약 시간
# timestamp = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())

def calc_time(lst:int):
    """
        마지막 요청 시간을 검사해서 2일 이상일 경우에 현재시간 기준 2일로 줄인다.
    """
    # 현재 시간 가져오기
    now = datetime.now()
    if (int(now.timestamp()) - int(lst)) > (86400 * 2):
        yesterday = now - timedelta(days=2)
        # yesterday_20h = yesterday.replace(hour=20, minute=0, second=0, microsecond=0)
        return int(yesterday.timestamp())
    else:
        return lst


def link_extractor(text):
    """
        텍스트에서 링크를 추출하는 함수
    """
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, text)
    if len(urls) == 0:
        return None
    return urls


def remove_link(text):
    """
        텍스트에서 링크를 제거하는 함수
    """
    # URL을 추출하는 정규 표현식
    url_pattern = r'https?://\S+'

    # 정규 표현식을 사용하여 URL 추출
    urls = re.findall(url_pattern, text)

    # 추출된 URL 출력
    for url in urls:
        text = text.replace(url, '')

    return text


def clean_text(text):
    cleaned_text = re.sub(r'\n+', ' ', text) # 줄바꿈을 빈칸으로 변경
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text) # 여러 빈칸을 하나의 빈칸으로

    if DEBUG_MODE:
        print("cleaned. ", len(cleaned_text), "characters") # 글자 수 출력

    return cleaned_text


async def gpt_summation(user_chat_id):
    """
        메시지를 가져오고
        GPT를 사용하여 요약한다
    
    """
    message_data_list = []
    me_entity = {}

    if userdata := USER_DB.get_data_db(user_chat_id=user_chat_id):
        username = userdata[1]
        me_entity = await bot.get_entity(f"https://t.me/{username}")
    # 마지막 요청 타임.

    lst = calc_time(lst=int(userdata[3]))

    # DB에서 유저가 등록한 채널 리스트를 가져온다
    dbdata = DB.getalldata_db(user_chat_id)
    if len(dbdata) == 0:
        await bot.send_message(me_entity, "⚠️ 현재 등록된 채널이 없습니다.\n/add [채널링크] 형식으로 입력하여 요약하실 채널을 추가해주세요.", parse_mode='html', link_preview=False)
        return
    await bot.send_message(me_entity, f"채널에서 메시지를 가져오는 중...", link_preview=False)
    channel_list = [i[1] for i in dbdata]

    # 채널 리스트를 돌면서 메시지를 확인한다
    res = ""
    cres = {}
    for count, channel in enumerate(channel_list, start=1):
        try:
            channel_info = await client.get_entity(channel) # 채널username 이 바뀌는 경우가 있음
        except Exception as e:
            LOG.error(f"channel_info - {e}")
            await bot.send_message(me_entity, f"🚨 채널 정보를 가져오는데 실패했습니다. 채널 링크가 우효하지 않거나 채널 링크가 변경 또는 사라진 경우 입니다.\n{channel} 을 확인해주시고 지속적으로 이 메시지가 표시될 경우 목록에서 제외해주세요.", link_preview=False)
            continue
        
        channel_info.id
        cres[channel_info.id] = ""
        msg_data = await client.get_messages(channel_info.id, 100) # , filter=InputMessagesFilterPhotos # 가장 마지막 메시지를 가져옴
        channel_info.title
        last_message_id = msg_data.total
        if res == "":
            res += f"{count}. <a href='https://t.me/{channel_info.username}'>{channel_info.title}</a>\n"
        else:
            res += f"\n\n\n{count}. <a href='https://t.me/{channel_info.username}'>{channel_info.title}</a>\n"
        
        for msg in reversed(msg_data):
            # print(msg.date.timestamp())
            if msg.date.timestamp() > int(lst): # 메시지 필터링
                message_time = str(datetime.fromtimestamp(msg.date.timestamp(), tz=ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S'))
                try:
                    data = {
                        "channel_id": channel_info.id,
                        "message_id": msg.id,
                        "channel_title": channel_info.title,
                        "channel_username": channel_info.username,
                        "timestamp": msg.date.timestamp(),
                        "date": message_time,
                        "message": clean_text(msg.text.replace('\n', ' ')), # "{} {}".format(message_time, clean_text(msg.text.replace('\n', ' '))),
                        "source": {
                            "origin_message_link": f"https://t.me/{channel_info.username}/{msg.id}",
                            "include_link": link_extractor(msg.text)
                        }
                    }

                    # print(data["message"])
                    message_data_list.append(data)
                except Exception as e:
                    LOG.error(f"gpt_summation - {e}")
                    continue
        
        # 20개씩 쪼갠다
        for i in range(0, len(message_data_list), 20):
            messages = message_data_list[i:i+20]
            req_text = ""
            for message in messages:
                
                # req_text += remove_link(message["message"]) + "\n\n"
                source = link_extractor(message["message"])
                if source:
                    req_text += remove_link(message["message"]) + " " + source[0] + " " + message['source']['origin_message_link'] + "\n\n" 
                else:
                    req_text += remove_link(message["message"]) + " " + message['source']['origin_message_link'] + "\n\n"
                    # req_text += remove_link(message["message"]) + " " + message['source']['origin_message_link'] + "\n\n"
            if DEBUG_MODE:
                with open(f"original/origin_input{str(int(time.time()))}.txt", "w", encoding="utf-8") as input_file:
                    input_file.write(req_text)
            # 요청 전송
            temp = await gpt_fetch.read_and_summarize(text=req_text)
            res += "\n\n" + temp
            
            cres[channel_info.id] += "\n\n" + temp
            if DEBUG_MODE:
                print(res)
            req_text = ""

        if message_data_list == []:
            continue
        message_data_list.clear()

    
    await bot.send_message(me_entity, f"ChatGPT 에게 요약을 요청하는 중...", link_preview=False)
    last = split_telegram_messages(data=res)
    for header, content in last:
        for count, x in enumerate(message_length_check(content)):
            if DEBUG_MODE:
                print(f"전송할 메시지 길이 : {len(x)}")
            x = x.replace("\n\n•", "•")
            x = x.replace("•", "\n\n•")
            x = x.replace("\n\n\n\n", "\n\n")
            if count == 0:
                await bot.send_message(me_entity, header + x, parse_mode='html', link_preview=False)
            else:
                await bot.send_message(me_entity, x, parse_mode='html', link_preview=False)

    USER_DB.update_data_db(user_chat_id=user_chat_id, last_summation_timestamp=int(time.time()))

    # 결과를 새로운 파일로 저장
    if DEBUG_MODE:
        with open(f"result/output{str(int(time.time()))}.txt", "w", encoding="utf-8") as output_file:
            output_file.write(res)

    if DEBUG_MODE:
        print(res)
        print("전송 완료")
    LOG.info("GPT Summation complete !")


def split_telegram_messages(data) -> list:
    result = []
    
    channel_pattern = re.compile(r'(\d+\.\s*<a href=[^>]+>.*?</a>\s*)(.*?)(?=\d+\.\s*<a href=|\Z)', re.DOTALL)
    for match in channel_pattern.finditer(data):
        header = match.group(1).strip()
        content = match.group(2).strip()
        if content == '':
            continue
        data = [
            header,
            content
        ]
        result.append(data)
        continue
    return result


def message_length_check(text) -> list:
    """
        메시지 길이 체크
        3900자를
    """
    try:
        z = text.split("•")
        z = list(set(z))

        res = []
        res2 = []

        for x in range(len(z)):
            if len("".join(res)) + len(z[x]) < 3900:
                res.append(z[x])
            else:
                res2.append("•".join(res))
                res.clear()
                res.append(z[x])
        
        res2.append("•".join(res))

        return res2
    except Exception as e:
        LOG.error(f"message_length_check - {e}")


# 봇 커맨드 명령어 핸들러
async def command_handler(event):
    """
        봇 커맨드 핸들러
    """
    try:
        if event.message.message == "/start":
            if not USER_DB.get_data_db(event.message.sender_id):
                # 등록
                reserve_data = {
                    "reserve_time": [
                        "08:00",
                        "20:00"
                    ] 
                }
                # 전날 8시로 기본값 세팅.
                now = datetime.now()
                yesterday = now - timedelta(days=1)
                yesterday_20h = yesterday.replace(hour=20, minute=0, second=0, microsecond=0)
                lst = int(yesterday_20h.timestamp())
                USER_DB.add_data_db(user_chat_id=event.message.sender_id, username=event.message._sender.username, reserved_time=json.dumps(reserve_data), last_summation_timestamp=lst)
                await event.reply("🎉 사용자 등록이 완료되었습니다. 봇 도움말은 /help 를 입력하세요.")
                return
            

            userdata = USER_DB.get_data_db(user_chat_id=event.message.sender_id)
            user_subs = DB.getalldata_db(chat_id=event.message.sender_id)
            ft = datetime.fromtimestamp(int(userdata[3]), tz=ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
            await event.reply(f"👨🏻‍💻 {ft} 이후의 채널 메시지 요약을 시작합니다.")
            s = time.time()
            await gpt_summation(user_chat_id=event.message.sender_id)
            await event.reply(f"👨🏻‍💻 요약이 완료되었습니다. {int(time.time() - s)}초 소요됨.")
            return


        elif event.message.message[:len("/add")] == "/add":
            try:
                channel_url = event.message.message.split(" ")[1]
                if re.match(r'^https?://', channel_url):
                    if DB.get_data_db(event.chat_id, channel_url):
                        await event.reply(f"⚠️ 이미 등록된 채널입니다. {channel_url}")
                        return
                    
                    else:
                        DB.add_data_db(event.chat_id, channel_url)
                        await event.reply(f"✅ 채널이 등록되었습니다. {channel_url}")
                        return
                else:
                    await event.reply("⚠️ /add [채널링크] 형식으로 입력해주세요.")
                    return

            except Exception as e:
                LOG.error(f"command_handler - /add {e}")
                await event.reply("⚠️ /add [채널링크] 형식으로 입력해주세요.")
                return  


        elif event.message.message[:len("/del")] == "/del":
            try:
                channel_url = event.message.message.split(" ")[1]
                if DB.get_data_db(event.chat_id, channel_url):
                    DB.delete_data_db(event.chat_id, channel_url)
                    await event.reply(f"💥 채널이 삭제되었습니다. {channel_url}")
                    return
                else:
                    await event.reply(f"⚠️ 존재하지 않는 채널입니다. {channel_url}")
                    return
            except Exception as e:
                LOG.error(f"command_handler - /del {e}")
                await event.reply("⚠️ /del [채널링크] 형식으로 입력해주세요.")
                return
            

        elif event.message.message == "/list":
            data = DB.getalldata_db(event.message.sender_id)
            message_list = []
            message_list.append("등록된 채널 목록 (채널명 - 등록일)\n\n")

            for chat_id, channel_url, date, ts in data:
                cdata = await client.get_entity(channel_url)
                message_list.append(f"<a href='{channel_url}'>{cdata.title}</a> - {date}\n\n")

            message = "".join(message_list)
            await event.reply(message, parse_mode='html', link_preview=False)
            return
        
        
        elif event.message.message[:len("/settime")] == "/settime":
            try:
                _, date_part, time_part = event.message.message.split()
                dt = datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M")
                timestamp = int(dt.timestamp())
                USER_DB.update_data_db(user_chat_id=event.message.sender_id, last_summation_timestamp=timestamp)
                await event.reply(f"요청 기준 시간이 {datetime.fromtimestamp(int(timestamp), tz=ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')} 로 변경 되었습니다.\n2일이 초과된 경우 그 이전의 메시지는 무시됩니다.")
                return

            except:
                await event.reply("/settime 2025-01-01 22:00\n위와 같은 형식으로 입력하세요.")
                return


        elif event.message.message == "/lt":
            """
                마지막 요약 시간을 반환한다.
            """
            userdata = USER_DB.get_data_db(user_chat_id=event.message.sender_id)
            ft = datetime.fromtimestamp(int(userdata[3]), tz=ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
            await event.reply(f"마지막 요약 시간 : {ft}")
            return


        elif event.message.message == "/updateuser":
            """
                user db 에 usernaeme db 를 업데이트한다
            """
            USER_DB.update_username_data_db(user_chat_id=event.message.sender_id, username=event.message._sender.username)
            await event.reply("유저핸들이 업데이트 되었습니다.")
            return
        

        elif event.message.message == "/quit":
            """
                quit 한다.
            """
            USER_DB.delete_data_db(user_chat_id=event.message.sender_id)
            await event.reply("더 이상 메시지가 수신되지 않습니다. 다시 등록하시려면 /start 를 입력하세요.")
            return


        elif event.message.message == "/help":
            helpmsg = """/start 요약 시작, 사용 등록
/add [채널링크] 채널 등록
/del [채널링크] 채널 삭제
/list 등록된 채널 확인
/settime 요약 시작 시점 설정
/lt 마지막 요약 시간
/updateuser 유저핸들 변경시 사용
/quit 봇 사용 종료
            """
            await event.reply(f"<code>{helpmsg}</code>", parse_mode="html")
            return

        elif event.message.message[:len("/target_channel")] == "/target_channel":
            try:
                c, channel_url = event.message.message.split()
                cdata = await client.get_entity(channel_url)
                cdata.id
                USER_DB.update_target_chat_id_data_db(event.message.sender_id, cdata.id)
                await event.reply(f"해당 채널에 봇을 추가하고 관리자로 등록하세요.\n요약 응답 채널이 변경되었습니다. {cdata.title}")
                await bot.send_message(cdata, "🤖 요약 데이터가 앞으로 이 채널로 전송됩니다.", parse_mode='html', link_preview=False)
            except Exception as e:
                LOG.error(f"target_channel command error - {e}")
                await event.reply("입력 형식이 올바르지 않습니다. /target_channel [채널링크]")
                return

    except Exception as e:
        LOG.error(f"command_handler - {e}")


def main():
    LOG.info("bot start")
    # 메인 실행 루프
    with client:
        # client.loop.run_until_complete(main())

        bot.loop.create_task(scheduler_loop.loop())

        # 봇 실행
        bot.start()

        bot.add_event_handler(command_handler, events.NewMessage())

        bot.run_until_disconnected()
        # # 대상 핸들러
        # client.add_event_handler(my_event_handler, events.NewMessage(chats=target_channel_id))
        # 세팅 핸들러
        # client.add_event_handler(command_event_handler, events.NewMessage())
        # 이벤트 처리를 위해 프로그램 실행 유지
        client.run_until_disconnected()

