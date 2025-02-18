import requests
import logging
import uuid
import config

# Функция для получения данных пользователя из базы
def get_user_from_db(user_id):
    try:
        headers = {
            "apikey": config.SUPABASE_API_KEY,
            "Authorization": f"Bearer {config.SUPABASE_API_KEY}"
        }
        url = f"{config.SUPABASE_URL}/rest/v1/users?vk_id=eq.{user_id}&select=*"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if response.json():
            return response.json()[0]
        return None
    except requests.RequestException as e:
        logging.error(f"Ошибка при получении данных пользователя {user_id}: {e}")
        return None

# Функция регистрации пользователя
def register_user(user_id):
    try:
        user_data = {
            "id": str(uuid.uuid4()),
            "username": f"User_{user_id}",
            "vk_id": user_id,
            "balance": 0.0,
            "created_at": "now()"
        }
        headers = {
            "Content-Type": "application/json",
            "apikey": config.SUPABASE_API_KEY,
            "Authorization": f"Bearer {config.SUPABASE_API_KEY}"
        }
        url = f"{config.SUPABASE_URL}/rest/v1/users"
        response = requests.post(url, json=user_data, headers=headers)
        response.raise_for_status()
        return response.status_code == 201
    except requests.RequestException as e:
        logging.error(f"Ошибка при регистрации пользователя {user_id}: {e}")
        return False

# Функция для обновления имени пользователя
def update_user_name(user_id, new_name):
    try:
        headers = {
            "Content-Type": "application/json",
            "apikey": config.SUPABASE_API_KEY,
            "Authorization": f"Bearer {config.SUPABASE_API_KEY}"
        }
        url = f"{config.SUPABASE_URL}/rest/v1/users?vk_id=eq.{user_id}"
        response = requests.patch(url, json={"username": new_name}, headers=headers)
        response.raise_for_status()
        return response.status_code == 200
    except requests.RequestException as e:
        logging.error(f"Ошибка при обновлении имени пользователя {user_id}: {e}")
        return False

# Функция для перевода средств между пользователями
def transfer_balance(from_user_id, to_user_id, amount):
    try:
        from_user = get_user_from_db(from_user_id)
        to_user = get_user_from_db(to_user_id)
        if not from_user or not to_user:
            return "❌ Один из пользователей не найден."
        if from_user['balance'] < amount:
            return "❌ Недостаточно средств для перевода."
        # Обновляем баланс отправителя
        new_balance_from = from_user['balance'] - amount
        headers = {
            "Content-Type": "application/json",
            "apikey": config.SUPABASE_API_KEY,
            "Authorization": f"Bearer {config.SUPABASE_API_KEY}"
        }
        response = requests.patch(f"{config.SUPABASE_URL}/rest/v1/users?id=eq.{from_user['id']}", 
                                  json={"balance": new_balance_from}, headers=headers)
        response.raise_for_status()
        # Обновляем баланс получателя
        new_balance_to = to_user['balance'] + amount
        response = requests.patch(f"{config.SUPABASE_URL}/rest/v1/users?id=eq.{to_user['id']}", 
                                  json={"balance": new_balance_to}, headers=headers)
        response.raise_for_status()
        return f"✅ Перевод {amount} средств пользователю {to_user['username']} выполнен успешно."
    except requests.RequestException as e:
        logging.error(f"Ошибка при переводе средств: {e}")
        return "❌ Ошибка при переводе средств. Попробуйте позже."
