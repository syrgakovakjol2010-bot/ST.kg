import os
import requests
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# --- КОНФИГУРАЦИЯ ---
# База данных sqlite (создаст файл в папке проекта)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spectech.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'st_kg_2026_secure'

db = SQLAlchemy(app)

# Данные для Telegram (берутся из переменных окружения для безопасности)
TELEGRAM_TOKEN = os.getenv("8769383770:AAHFu2sduzBpr1-er9C59lWMh7r1499rDkg")
CHAT_ID = os.getenv("5385396977")

# --- МОДЕЛИ БАЗЫ ДАННЫХ ---

class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    tech_type = db.Column(db.String(50))
    specs = db.Column(db.Text) # Характеристики: г/п, объем и т.д.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(50))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- ФУНКЦИИ ---

def send_telegram_notification(message):
    """Отправка уведомления в твой Телеграм"""
    if TELEGRAM_TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            print(f"Ошибка Telegram: {e}")

# --- МАРШРУТЫ (ROUTES) ---

@app.route('/')
def index():
    # Главная страница (должна лежать в templates/index.html)
    return render_template('index.html')

@app.route('/api/register_partner', methods=['POST'])
def register_partner():
    try:
        data = request.json
        name = data.get('name')
        phone = data.get('phone')
        tech_type = data.get('tech_type')
        specs = data.get('specs', {})

        # Сохраняем в базу данных
        new_partner = Partner(
            name=name,
            phone=phone,
            tech_type=tech_type,
            specs=str(specs)
        )
        db.session.add(new_partner)
        db.session.commit()

        # Формируем сообщение для Телеграм
        tg_msg = (
            f"🚜 <b>НОВЫЙ ПАРТНЕР (ST.kg)</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"📞 <b>Тел:</b> {phone}\n"
            f"🏗 <b>Техника:</b> {tech_type}\n"
            f"📋 <b>Данные:</b> {specs}\n"
        )
        send_telegram_notification(tg_msg)

        return jsonify({"status": "success", "message": "Заявка принята!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/ai_chat', methods=['POST'])
def ai_chat():
    user_msg = request.json.get('message', '').lower()
    
    # Логика быстрых ответов (заглушка под ИИ)
    if "кран" in user_msg or "поднять" in user_msg:
        reply = "В выбранном регионе доступны автокраны 16т и 25т. Какой груз планируете поднимать?"
    elif "копать" in user_msg or "фундамент" in user_msg:
        reply = "Рекомендую заказать экскаватор-погрузчик. Он приедет быстрее всего. Оформить заказ?"
    elif "бетон" in user_msg or "залить" in user_msg:
        reply = "У нас есть бетоносмесители и насосы. Укажите объем в м³, чтобы я рассчитал количество машин."
    else:
        reply = "Я помогу подобрать технику. Опишите задачу или просто напишите, что вам нужно вывезти или построить."

    return jsonify({"reply": reply})

# --- ЗАПУСК ПРИЛОЖЕНИЯ ---

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Создает базу данных, если её нет
    
    # Для работы на сервере/телефоне используем 0.0.0.0
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
    
