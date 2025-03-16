import telebot
from config import *
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from modules.logic import DB_Map
import os



    
bot = telebot.TeleBot(TOKEN)
# Функция для создания основной клавиатуры
def create_main_keyboard():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = "Помощь"
    markup.add(button1)
    return markup
# Функция для создания клавиатуры с кнопками inline
def create_inline_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Город 1", callback_data="city1")
    button2 = InlineKeyboardButton("Город 2", callback_data="city2")
    markup.add(button1, button2)
    return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(
        message.chat.id, 
        "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.", 
        reply_markup=create_main_keyboard()  # Кнопки для удобства
    )

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(
        message.chat.id, 
        "Доступные команды:\n/show_city <город> - Показать город на карте\n/remember_city  - Запомнить город\n/show_my_cities - Мои города\n/show_my_cities - Мои города  Соединить города\n/line",
        reply_markup=create_main_keyboard()  # Кнопки для удобства
    )



@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    # Отправка сообщения с пояснением и клавиатурой для выбора города
    city_name = message.text.split()[-1]  # Извлекаем название города
    user_id = message.chat.id
    coordinates = manager.get_coordinates(city_name)
    
    if coordinates:  # Если координаты найдены
        manager.create_grapf(f'{user_id}.png', {city_name: coordinates})
        with open(f'{user_id}.png', 'rb') as img:
            bot.send_photo(user_id, img, reply_markup=create_main_keyboard())  # Кнопки после отправки фото
    else:
        bot.send_message(
            user_id, 
            f'Город {city_name} не найден. Проверьте правильность написания.',
            reply_markup=create_main_keyboard()  # Кнопки после ошибки
        )


@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split()[-1]
    
    if manager.add_city(user_id, city_name):
        bot.send_message(
            message.chat.id, 
            f'Город {city_name} успешно сохранен!',
            reply_markup=create_main_keyboard()  # Кнопки после добавления города
        )
    else:
        bot.send_message(
            message.chat.id, 
            'Такого города я не знаю. Убедись, что он написан на английском!',
            reply_markup=create_main_keyboard()  # Кнопки после ошибки
        )

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    # Получаем список городов из базы данных
    cities = manager.select_cities(message.chat.id)
    
    if cities:
        user_id = message.chat.id
        
        # Создаем словарь, где ключом будет название города, а значением его координаты
        city_coordinates = {city: manager.get_coordinates(city) for city in cities}
        
        # Передаем словарь в create_grapf
        manager.create_grapf(f'{user_id}.png', city_coordinates)
        
        # Отправляем картинку пользователю
        with open(f'{user_id}.png', 'rb') as img:
            bot.send_photo(user_id, img, reply_markup=create_main_keyboard())  # Кнопки после отправки фото
    else:
        bot.send_message(
            message.chat.id,
            'Не удалось найти запомненные города.',
            reply_markup=create_main_keyboard()  # Кнопки после ошибки
        )

        
       
@bot.message_handler(commands=['line'])
def line(message):
    # Извлекаем два города из сообщения
    user_id = message.chat.id
    cities = message.text.split()[1:]  # Получаем список городов (убираем /line)
    
    if len(cities) != 2:
        bot.send_message(user_id, "Пожалуйста, укажите два города через пробел.")
        return

    city1, city2 = cities
    coordinates1 = manager.get_coordinates(city1)
    coordinates2 = manager.get_coordinates(city2)

    if coordinates1 and coordinates2:  # Если координаты обоих городов найдены
        # Используем уникальный файл для каждого пользователя
        file_path = f"{user_id}_line.png"  # Создаем путь к файлу с уникальным именем
        manager.draw_distance(city1, city2, file_path)  # Рисуем линию и сохраняем картинку

        # Отправляем изображение пользователю
        with open(file_path, 'rb') as img:
            bot.send_photo(user_id, img, reply_markup=create_main_keyboard(), timeout=60)
    else:
        bot.send_message(user_id, f"Не удалось найти координаты")



@bot.message_handler(func=lambda message: True) 
def handle_text(message):
    
 
    if message.text == "Помощь":
        bot.send_message(
            message.chat.id, 
            "Напиши /help для списка команд.",
            reply_markup=create_main_keyboard()  # Кнопки для дальнейших действий
        )


if __name__=="__main__":
    manager = DB_Map(DATABASE)
    
    # Запуск бота
    bot.polling()

