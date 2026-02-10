import asyncio
import time
import json
from app import bot
from datetime import datetime
from zoneinfo import ZoneInfo


# 08:00 형식을 오늘기준 타임스탬프로 변환 하는코드
def convert_time(timestamp, reserved_time:str):

    hour, minute = reserved_time.split(":")
    now = datetime.fromtimestamp(timestamp, tz=ZoneInfo('Asia/Seoul'))# .strftime('%Y-%m-%d %H:%M:%S')
    # yesterday = now - timedelta(days=1)
    converted_yesterday = now.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
    # if bot.DEBUG_MODE:
    #     print(timestamp, " - ", int(converted_yesterday.timestamp()), f"left in {int(converted_yesterday.timestamp()) - timestamp} sec")
    return int(converted_yesterday.timestamp())


async def loop():
    """
        스케쥴러임 비동기 처리 필요.
    """
    """
    """
    bot.LOG.info("Scheduler loop start...")

    while True:
        try:
        
            st_timestamp = int(time.time())

            for userdata in bot.USER_DB.getalldata_db():
                sc = json.loads(userdata[2])

                for x in sc.get("reserve_time", []):
                    if int(convert_time(st_timestamp, x)) == int(st_timestamp):
                        bot.bot.loop.create_task(bot.gpt_summation(user_chat_id=userdata[0]))

            await asyncio.sleep(1)

        except Exception as e:
            bot.LOG.error(f"scheduler loop error! {e}")
