import os
import requests
import random
import telebot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

current_image_index = 0  # Текущий индекс изображения

def get_image_url(query):
    url = 'https://api.pexels.com/v1/search'
    headers = {'Authorization': os.getenv('PEXELS_API_KEY')}
    params = {'query': query, 'orientation': 'portrait'}
    response = requests.get(url, headers=headers, params=params)
    results = response.json()['photos']
    if len(results) == 0:
        return None
    photo = random.choice(results)
    return photo['src']['medium']

def get_random_images():
    images = []
    for query in ['car', 'nature', 'animal', 'city']:
        url = get_image_url(query)
        images.append(url)
    random.shuffle(images)
    return images

def send_random_image(chat_id, images):
    global current_image_index  # Используем глобальную переменную

    # Обновляем текущий индекс изображения
    current_image_index = (current_image_index) % len(images)

    # Создаем клавиатуру с кнопкой "New Photo"
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text='New Photo', callback_data='new_photo'))

    # Отправляем новое изображение
    bot.send_photo(chat_id, images[current_image_index], caption=f'Image {current_image_index}', reply_markup=keyboard)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Send me '/images' to get a random image.")

@bot.message_handler(commands=['images'])
def send_images(message):
    chat_id = message.chat.id
    images = get_random_images()

    # Отправляем первое изображение
    send_random_image(chat_id, images)

@bot.callback_query_handler(func=lambda call: call.data == 'new_photo')
def handle_new_photo(call):
    chat_id = call.message.chat.id
    images = get_random_images()

    # Отправляем новое изображение
    send_random_image(chat_id, images)

bot.polling()
