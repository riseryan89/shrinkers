from typing import Text
import requests
from shortener.models import Schedules, ShortenedUrls, Users

access_token = "1978567738:AAE8Fz3s8keXVeZrxDlAXJ2c0rOpx1HAOSg"


def get_chats():
    uri = f"https://api.telegram.org/bot{access_token}/getUpdates"
    res = requests.get(uri).json()
    return res.get("result") if res.get("ok") else []


def chat_handler():
    msgs = get_chats()
    scheduler = Schedules.objects.filter(id=1)
    latest_ts = scheduler.first().value
    final_ts = 0
    chats = {}
    for m in msgs:
        msg = m.get("message")
        chat = msg.get("chat", {})
        chat_ts = msg.get("date", 0)
        if chat_ts > latest_ts:
            chat_id = chat.get("id")
            matched_user = Users.objects.filter(telegram_username=chat_id).first()
            if not matched_user:
                continue
            if chats.get(matched_user.id):
                chats[matched_user.id].append(str(msg.get("text", "")))
            else:
                chats[matched_user.id] = [str(msg.get("text", ""))]

            if chat_ts > latest_ts:
                final_ts = chat_ts

    if final_ts > latest_ts:
        scheduler.update(value=final_ts)

    return chats


def send_chat(chat_id: str, msg: str):
    uri = f"https://api.telegram.org/bot{access_token}/sendMessage"
    body = {"chat_id": chat_id, "text": msg}
    res = requests.post(uri, data=body)


def get_response(command, url=None):
    c = {
        "start": "/help 로 안내를 받아보세요!",
        "help": "/short [닉네임] [목적지 url] 형식으로 입력하시면 단축 URL 이 제공됩니다.",
        "done": f"완성되었어요! {url}",
    }
    return c.get(command, "잘 못 알아들었습니다. /help 로 도움말을 참고하세요.")


def command_handler():
    chats = chat_handler()
    for key, val in chats.items():
        user_info = Users.objects.filter(id=key).first()
        for v in val:
            if v == "/start":
                send_chat(user_info.telegram_username, get_response("start"))
            elif v == "/help":
                send_chat(user_info.telegram_username, get_response("help"))
            elif v.startswith("/short "):
                get_text = v.strip().split(" ")
                nick_name = get_text[1]
                target_url = get_text[2]

                url = ShortenedUrls()
                url.nick_name = nick_name
                url.creator = user_info
                url.target_url = target_url
                url.create_via = "telegram"
                url.save()

                send_chat(
                    user_info.telegram_username,
                    get_response("done", url=f"http://localhost:8000/{url.prefix}/{url.shortened_url}"),
                )


"""
{
   "update_id":146456873,
   "message":{
      "message_id":6,
      "from":{
         "id":606139543,
         "is_bot":false,
         "first_name":"shrinkers",
         "username":"shrinkers",
         "language_code":"ko"
      },
      "chat":{
         "id":606139543,
         "first_name":"shrinkers",
         "username":"shrinkers",
         "type":"private"
      },
      "date":1630207549,
      "text":"ㅇ"
   }
}
"""
