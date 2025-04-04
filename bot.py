import os
import requests
import time
import telebot
from bs4 import BeautifulSoup

# Telegram bot token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Беремо токен із змінних середовища
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # ID чату, куди надсилати повідомлення
bot = telebot.TeleBot(TOKEN)

# URL-адреси товарів
targets = {
    "Chunky Sneakers": "https://www.showroom.pl/p-chunky-sneakers-z-podwojnym-zamknieciem-jezyka-230984c8-677a-4c63-b037-9aac488616bf",
    "Track Sneakers": "https://www.showroom.pl/p-track-sneakers-a391aa6b-6a78-4511-9613-c92311d64844"
}

# Відстежувані розміри
sizes_to_track = {"36", "37"}

# Збережені ціни та наявні розміри
previous_data = {}

def check_prices():
    global previous_data
    
    for name, url in targets.items():
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Отримання ціни
        price_tag = soup.find("span", class_="price-value")
        price = price_tag.text.strip() if price_tag else "N/A"
        
        # Отримання доступних розмірів
        sizes = set()
        size_elements = soup.find_all("button", class_="size-button")
        for size in size_elements:
            if "disabled" not in size.attrs:
                sizes.add(size.text.strip())
        
        # Перевірка змін
        old_price, old_sizes = previous_data.get(name, (None, set()))
        if old_price != price or sizes_to_track - old_sizes != set():
            message = f"🔔 {name} оновлено!\n💰 Ціна: {price}\n📏 Доступні розміри: {', '.join(sizes) or 'Немає'}\n🔗 {url}"
            bot.send_message(CHAT_ID, message)
        
        previous_data[name] = (price, sizes)

while True:
    check_prices()
    time.sleep(1800)  # Перевірка кожні 30 хвилин
