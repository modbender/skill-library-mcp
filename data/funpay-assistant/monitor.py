
import sys
import time
import json
import os
import requests
from FunPayAPI.account import Account

# Установка UTF-8
sys.stdout.reconfigure(encoding='utf-8')

GOLDEN_KEY = "r7sb47vn2sq6vhziu7veeh8eh31j02bz"
STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")

# Тексты ответов
REGION_ERROR_REPLY = "К сожалению, по правилам FunPay запрещает упоминать любые прокси или VPN сервисы. Если в вашем впне нет региона Чили, то могу предложить такой вариант: Я захожу к вам на аккаунт и активирую ваш ключ."
AVAILABILITY_REPLY = "Да, в наличии."
HERE_REPLY = "Да, на связи."

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"last_message_texts": {}, "auto_replied_chats": []}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

# Временная заплатка для метода send_message, который ломается на парсинге ответа
def safe_send_message(acc, chat_id, text):
    try:
        acc.send_message(chat_id, text)
    except AttributeError:
        # Игнорируем ошибку парсинга HTML, если запрос ушел успешно
        pass
    except Exception as e:
        print(f"Ошибка отправки в чат {chat_id}: {e}")

def check_funpay():
    state = load_state()
    acc = Account(GOLDEN_KEY).get()
    chats = acc.request_chats()
    
    notifications = []
    
    for chat in chats:
        chat_id = str(chat.id)
        msg_text = getattr(chat, 'last_message_text', None)
        
        if msg_text is None:
            continue
            
        last_msg_lower = msg_text.lower()
        
        # Проверка дубликатов
        if state["last_message_texts"].get(chat_id) == msg_text:
            continue
            
        state["last_message_texts"][chat_id] = msg_text
        
        # 1. Проверка на жалобы по региону/активации
        if any(x in last_msg_lower for x in ["не получается", "недоступно", "регион", "чили", "впн", "vpn", "ошибка"]):
            safe_send_message(acc, chat.id, REGION_ERROR_REPLY)
            if chat_id not in state["auto_replied_chats"]:
                state["auto_replied_chats"].append(chat_id)
            print(f"DEBUG: Ответил на проблему в чате {chat.name}")
            continue

        # 2. Проверка на согласие
        if chat_id in state["auto_replied_chats"]:
            if any(x in last_msg_lower for x in ["давай", "согласен", "заходи", "окей", "ок", "хорошо"]):
                notifications.append(f"🔔 СРОЧНО: Покупатель {chat.name} согласен на вход в аккаунт! (ID: {chat_id})")
                state["auto_replied_chats"].remove(chat_id)
                continue

        # 3. Проверка на "Ты тут?" / "В наличии?"
        if any(x in last_msg_lower for x in ["тут", "здесь", "на связи", "ты тут"]):
            safe_send_message(acc, chat.id, HERE_REPLY)
            continue
        if any(x in last_msg_lower for x in ["в наличии", "есть?", "актуально"]):
            safe_send_message(acc, chat.id, AVAILABILITY_REPLY)
            continue

        # 4. Пересылка админу
        if "подтвердил успешное выполнение заказа" not in last_msg_lower:
             notifications.append(f"📩 Сообщение от {chat.name}:\n\"{msg_text}\"\n(ID: {chat_id})")

    save_state(state)
    return notifications

if __name__ == "__main__":
    try:
        results = check_funpay()
        for note in results:
            print(f"NOTIFY: {note}")
    except Exception as e:
        import traceback
        traceback.print_exc()
