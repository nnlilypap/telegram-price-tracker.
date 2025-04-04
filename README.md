import telebot
import requests
from bs4 import BeautifulSoup
import time
import json

# Токен бота і ID чату
API_TOKEN = 'YOUR_BOT_API_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'

# Створення об'єкта бота
bot = telebot.TeleBot(API_TOKEN)

# Словник для зберігання підписок
subscriptions = {}

# Функція для збереження підписок
def save_subscriptions():
    with open("subscriptions.json", "w") as f:
        json.dump(subscriptions, f)

# Функція для завантаження підписок
def load_subscriptions():
    global subscriptions
    try:
        with open("subscriptions.json", "r") as f:
            subscriptions = json.load(f)
    except FileNotFoundError:
        subscriptions = {}

# Парсинг сторінки товару
def check_price_and_size(url, sizes):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Твої CSS-селектори для ціни та наявних розмірів
        price = soup.find('span', {'class': 'product-price'})  # Заміни на правильний селектор
        available_sizes = soup.find_all('span', {'class': 'size'})  # Заміни на правильний селектор
        
        available_sizes = [size.get_text() for size in available_sizes]
        price = price.get_text() if price else 'Ціна не знайдена'

        # Перевірка на наявність потрібних розмірів
        sizes_found = [size for size in sizes if size in available_sizes]
        
        return price, sizes_found
    except Exception as e:
        return None, None

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привіт! Надай лінк на товар, щоб почати відстеження.")

# Команда для додавання товару
@bot.message_handler(commands=['add'])
def add_product(message):
    msg = bot.reply_to(message, "Надішли лінк на товар для відстеження.")
    bot.register_next_step_handler(msg, process_url)

def process_url(message):
    url = message.text
    msg = bot.reply_to(message, "Який розмір(и) потрібно відстежувати? Напиши через кому (наприклад, 36, 37):")
    bot.register_next_step_handler(msg, process_sizes, url)

def process_sizes(message, url):
    sizes = message.text.split(',')
    sizes = [size.strip() for size in sizes]
    
    if url not in subscriptions:
        subscriptions[url] = sizes
        save_subscriptions()

    bot.reply_to(message, f"Відстежую товар {url} для розмірів: {', '.join(sizes)}.")
    start_tracking(url, sizes)

# Відстежування зміни ціни та розмірів
def start_tracking(url, sizes):
    while True:
        price, sizes_found = check_price_and_size(url, sizes)
        if price and sizes_found:
            message = f"Товар: {url}\nЦіна: {price}\nДоступні розміри: {', '.join(sizes_found)}"
            bot.send_message(CHAT_ID, message)
        time.sleep(3600)  # Перевіряти кожні 60 хвилин

# Команда /unsubscribe для скасування підписки
@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    msg = bot.reply_to(message, "Введи лінк на товар, для якого хочеш скасувати підписку.")
    bot.register_next_step_handler(msg, remove_subscription)

def remove_subscription(message):
    url = message.text
    if url in subscriptions:
        del subscriptions[url]
        save_subscriptions()
        bot.reply_to(message, f"Підписка на товар {url} скасована.")
    else:
        bot.reply_to(message, "Товар не знайдено серед підписок.")

# Запуск бота
load_subscriptions()
bot.polling()
