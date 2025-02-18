import vk_api
import json
import re
import logging
import db
import config
import datetime

# Клавиатуры
keyboard_auth = json.dumps({
    "one_time": False,
    "buttons": [
        [
            {"action": {"type": "text", "label": "📝 Регистрация"}, "color": "positive"},
            {"action": {"type": "text", "label": "🔑 Вход"}, "color": "primary"}
        ]
    ]
}, ensure_ascii=False)

keyboard_main = json.dumps({
    "one_time": False,
    "buttons": [
        [{"action": {"type": "text", "label": "💬 Игровые чаты"}, "color": "positive"}],
        [{"action": {"type": "text", "label": "⚙ Настройки акка"}, "color": "primary"}],
        [{"action": {"type": "text", "label": "⚡ Пополнить"}, "color": "primary"},
         {"action": {"type": "text", "label": "📤 Перевести"}, "color": "primary"}],
        [{"action": {"type": "text", "label": "📊 История операций"}, "color": "positive"}],
        [{"action": {"type": "text", "label": "🔥 Топ дня"}, "color": "negative"},
         {"action": {"type": "text", "label": "🌿 Топ недели"}, "color": "negative"}],
        [{"action": {"type": "text", "label": "🎁 Топ кланов"}, "color": "negative"}],
        [{"action": {"type": "text", "label": "📘 Как играть?"}, "color": "secondary"}],
        [{"action": {"type": "text", "label": "🔗 Telegram"}, "color": "primary"},
         {"action": {"type": "text", "label": "🔑 Сайт"}, "color": "primary"}]
    ]
}, ensure_ascii=False)

keyboard_settings = json.dumps({
    "inline": True,
    "buttons": [
        [
            {"action": {"type": "text", "label": "Смена имени"}, "color": "primary"},
            {"action": {"type": "text", "label": "Верификация"}, "color": "primary"}
        ],
        [
            {"action": {"type": "text", "label": "Скрыть баланс"}, "color": "primary"},
            {"action": {"type": "text", "label": "Скрыть кнопки ставок"}, "color": "primary"}
        ],
        [
            {"action": {"type": "text", "label": "Тег клана"}, "color": "primary"},
            {"action": {"type": "text", "label": "API"}, "color": "primary"}
        ]
    ]
}, ensure_ascii=False)

keyboard_top_up = json.dumps({
    "inline": True,
    "buttons": [
        [
            {"action": {"type": "open_link", "label": "Ручная продажа", "link": "https://example.com/manual_sale"}}
        ]
    ]
}, ensure_ascii=False)

keyboard_games = json.dumps({
    "inline": True,
    "buttons": [
        [
            {"action": {"type": "open_link", "label": "Wheel", "link": "https://vk.me/join/AZQ1dyaZOQbpCxc9EP3iY2pz"}},
            {"action": {"type": "open_link", "label": "Wheel Lightning", "link": "https://vk.me/join/AZQ1dyaZOQbpCxc9EP3iY2pz"}}
        ],
        [
            {"action": {"type": "open_link", "label": "Blackjack", "link": "https://vk.me/join/AZQ1dyaZOQbpCxc9EP3iY2pz"}},
            {"action": {"type": "open_link", "label": "Mines", "link": "https://vk.me/join/AZQ1dyaZOQbpCxc9EP3iY2pz"}}
        ],
        [
            {"action": {"type": "open_link", "label": "Slot", "link": "https://vk.me/join/AZQ1dyaZOQbpCxc9EP3iY2pz"}},
            {"action": {"type": "open_link", "label": "Tower", "link": "https://vk.me/join/AZQ1dyaZOQbpCxc9EP3iY2pz"}}
        ],
        [
            {"action": {"type": "open_link", "label": "Coin", "link": "https://vk.me/join/AZQ1dyaZOQbpCxc9EP3iY2pz"}},
            {"action": {"type": "open_link", "label": "Richer", "link": "https://vk.me/join/AZQ1dyaZOQbpCxc9EP3iY2pz"}}
        ]
    ]
}, ensure_ascii=False)

# Функция для отображения настроек и профиля пользователя
def show_profile_and_settings(user_id, vk):
    profile = db.get_user_from_db(user_id)
    if profile:
        # Форматируем дату регистрации (ожидается формат ISO, например, 2025-02-18T10:21:32.744062)
        try:
            reg_date = datetime.datetime.strptime(profile['created_at'], '%Y-%m-%dT%H:%M:%S.%f').strftime('%d.%m.%Y')
        except Exception:
            reg_date = profile['created_at']
        message = (
            f"[vk.com/id{profile['vk_id']}|{profile['username']}]\n\n"
            f"Ранг: {profile.get('role', 'неизвестно')}\n\n"
            f"Баланс: {profile['balance']}\n\n"
            f"Сумма всех ставок: {profile.get('total_bets', 0)}\n"
            f"Количество побед: {profile.get('total_wins', 0)}\n\n"
            f"Дата регистрации: {reg_date}\n\n"
            "Крути верти настраивай:"
        )
        send_message(vk, user_id, message, keyboard_settings)
    else:
        send_message(vk, user_id, "❌ Профиль не найден. Для регистрации напишите '📝 регистрация'.")

# Функция отправки сообщения
def send_message(vk, user_id, text, keyboard=None):
    vk.messages.send(user_id=user_id, message=text, random_id=0, keyboard=keyboard)
    logging.info(f"Сообщение отправлено пользователю {user_id}: {text}")

# Функция для смены имени
def start_name_change(user_id, vk):
    send_message(vk, user_id, "Введите новое имя:")

def change_name(user_id, new_name, vk):
    if db.update_user_name(user_id, new_name):
        send_message(vk, user_id, f"✅ Ваше имя изменено на {new_name}.")
    else:
        send_message(vk, user_id, "❌ Ошибка при изменении имени. Попробуйте позже.")

# Функция для обработки команды перевода средств
def handle_transfer(user_id, message_text, vk, awaiting_transfer):
    state = awaiting_transfer[user_id]
    if state["step"] == "link":
        match = re.search(r"(id\d+|[^/\s@]+)$", message_text)
        if match:
            to_user_identifier = match.group(1)
            state["to_user"] = to_user_identifier
            state["step"] = "amount"
            send_message(vk, user_id, "Какую сумму вы хотите перевести?")
        else:
            send_message(vk, user_id, "❌ Неправильный формат ссылки. Используйте: vk.com/id12345 или @username")
    elif state["step"] == "amount":
        try:
            amount = float(message_text)
            to_user_identifier = state["to_user"]
            # Определяем, является ли идентификатор числовым (id) или username
            if to_user_identifier.isdigit():
                to_user_id = int(to_user_identifier)
            else:
                # Запросим пользователя по username из базы
                headers = {
                    "apikey": config.SUPABASE_API_KEY,
                    "Authorization": f"Bearer {config.SUPABASE_API_KEY}"
                }
                url = f"{config.SUPABASE_URL}/rest/v1/users?username=eq.{to_user_identifier}&select=vk_id"
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                json_resp = response.json()
                if json_resp:
                    to_user_id = json_resp[0]["vk_id"]
                else:
                    send_message(vk, user_id, "❌ Пользователь не найден.")
                    del awaiting_transfer[user_id]
                    return
            result = db.transfer_balance(user_id, to_user_id, amount)
            send_message(vk, user_id, result)
            if "✅" in result:
                send_message(vk, to_user_id, f"✅ Вы получили {amount} средств от пользователя {user_id}.")
            del awaiting_transfer[user_id]
        except ValueError:
            send_message(vk, user_id, "❌ Неправильный формат суммы. Введите число.")
