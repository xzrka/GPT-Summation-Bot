# GPT_Summation_Bot
특정 시간동안 발송된 다수의 텔레 채널 메세지를 한 줄 요약해주는 텔레 봇
=======
# 🤖 GPT Summation Bot
> **여러 텔레그램 채널의 뉴스를 수집하여 GPT-4o-mini로 중복 없는 한 줄 요약을 제공하는 자동화 봇**

본 프로젝트는 실제 의뢰 기반 요구사항을 충족하기 위해 개발된 **포트폴리오용 프로젝트**입니다. 정보 과잉 시대에 사용자가 구독 중인 여러 채널의 핵심 뉴스만을 선별하여 정기적으로 리포트합니다.

---

## 🌟 주요 특징 (Key Features)

* **다중 채널 통합 요약**: 사용자별로 등록된 N개의 채널 메시지를 한 번에 수집 및 분석합니다.
* **스마트 필터링**: 마지막 요약 시점 이후의 메시지만 수집하며, 데이터 과부하 방지를 위해 **최근 2일치 제한** 로직을 포함합니다.
* **지능형 중복 제거**: 여러 채널에서 동일한 이슈를 다룰 경우, LLM이 이를 감지하여 최종 결과물에는 단일 요약본만 표시합니다.
* **가독성 중심 인터페이스**: 채널별 섹션 분리, 하이퍼링크 포함, 불릿 포인트 기반의 한 줄 요약 형식을 제공합니다.
* **정기 자동화 스케줄러**: 매일 `08:00`, `20:00` 정해진 시간에 자동으로 요약 리포트를 발송합니다.

---

## 🛠 기술 스택 (Tech Stack)

| 구분 | 기술 |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **API / LLM** | OpenAI API (`gpt-4o-mini`), [Telethon](https://github.com/LonamiWebs/Telethon) |
| **Database** | SQLite3 (File-based) |
| **Async / Schedule** | `asyncio`, Custom Polling Scheduler |
| **Tools** | `python-dotenv`, `tiktoken` (Token Counting), `logging` |

---

## 📂 디렉터리 구조 (Architecture)



```text
GPT_summation_bot/
├─ app/
│  ├─ bot.py            # Bot 진입점 및 명령어 핸들링
│  ├─ gpt_fetch.py      # Prompt Engineering 및 OpenAI API 연동
│  ├─ database.py       # SQLite CRUD 래퍼 클래스
│  ├─ scheduler_loop.py # 정기 요약 실행 스케줄러
│  └─ logger.py         # 공용 로깅 모듈
├─ database/            # 사용자 설정 및 구독 목록 (SQLite DB)
├─ original/ / result/  # 디버깅용 텍스트 저장 폴더 (Debug 모드 전용)
├─ session/             # Telethon 세션 데이터 저장 폴더
├─ run.py               # 메인 실행 스크립트
└─ .env                 # API 키 및 환경 변수 관리
```


## 라이선스

이 코드는 실제 상용 프로젝트를 기반으로 한 **포트폴리오용 공개**입니다.  
별도의 서면 허가 없이 사용·복제·배포·변경할 수 없습니다.