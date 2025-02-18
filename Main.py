import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import logging
import config
import db
import handlers

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация VK API
vk_session = vk_api.VkApi(token=config.TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, config.GROUP_ID)

# Основной цикл работы бота
print("[LOG] Бот запущен!")
awaiting_transfer = {}  # хранит состояния перевода: {user_id: {"step": str, "to_user": str}}

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_id = event.obj.message["from_id"]
        message_text = event.obj.message["text"].strip()
        logging.info(f"Новое сообщение от {user_id}: {message_text}")
        profile = db.get_user_from_db(user_id)

        if message_text.lower() == "начать":
            if profile:
                handlers.send_message(vk, user_id, "🚀 Добро пожаловать в RDMD GAMES!", handlers.keyboard_main)
            else:
                handlers.send_message(vk, user_id, "🚀 Добро пожаловать в RDMD GAMES!\nВыберите действие:", handlers.keyboard_auth)

        elif message_text.lower() == "📝 регистрация":
            if profile:
                handlers.send_message(vk, user_id, "❌ Вы уже зарегистрированы.", handlers.keyboard_main)
            elif db.register_user(user_id):
                handlers.send_message(vk, user_id, "✅ Регистрация успешна!", handlers.keyboard_main)
            else:
                handlers.send_message(vk, user_id, "❌ Ошибка регистрации. Попробуйте позже.")

        elif message_text.lower() == "🔑 вход":
            if profile:
                handlers.send_message(vk, user_id, "✅ Вы успешно вошли в систему!", handlers.keyboard_main)
            else:
                handlers.send_message(vk, user_id, "❌ Профиль не найден. Для регистрации напишите '📝 регистрация'.", handlers.keyboard_auth)

        elif message_text.lower() == "💬 игровые чаты":
            # Выводим клавиатуру с играми
            handlers.send_message(vk, user_id, "Выберите режим игры:", handlers.keyboard_games)

        elif message_text.lower() == "⚙ настройки акка":
            handlers.show_profile_and_settings(user_id, vk)

        elif message_text.lower() == "✏ сменить имя":
            handlers.start_name_change(user_id, vk)

        # Обработка смены имени, если пользователь уже в процессе изменения
        elif profile and profile.get("changing_name", False):
            handlers.change_name(user_id, message_text, vk)

        elif message_text.lower() == "⚡ пополнить":
            handlers.send_message(vk, user_id, "Список доступных маркетов:", handlers.keyboard_top_up)

        elif message_text.lower() == "📤 перевести":
            awaiting_transfer[user_id] = {"step": "link"}
            handlers.send_message(vk, user_id, 
                "Кому вы хотите перевести? Отправьте ссылку на игрока.\n\n"
                "Примеры ссылки:\nhttps://vk.com/redaimid\nvk.com/redaimid\n@redaimid\n"
                "https://vk.com/id12345\nvk.com/id12345\n@id12345")

        elif user_id in awaiting_transfer:
            handlers.handle_transfer(user_id, message_text, vk, awaiting_transfer)

        # Если сообщение не соответствует ни одному условию, можно добавить обработку inline payload и другие команды
        else:
            # По умолчанию возвращаем главное меню
            handlers.send_message(vk, user_id, "Неизвестная команда. Используйте главное меню.", handlers.keyboard_main)
