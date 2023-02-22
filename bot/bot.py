import sys
sys.path.append('..')

import os

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import bs4
import json
import requests

bot = telebot.TeleBot("6003211846:AAEjXt3qDu1df4zXEZT0OF41a0cCzyIBlYQ", parse_mode=None)

url = 'https://5689-188-126-76-166.eu.ngrok.io'
admin_id = 128596867

def webAppKeyboard(user_id): #создание клавиатуры с webapp кнопкой
    keyboard = types.ReplyKeyboardMarkup(row_width=4, resize_keyboard=True) #создаем клавиатуру
    webAppTest = types.WebAppInfo(f"{url}/?user_id={user_id}") #создаем webappinfo - формат хранения url
    button = types.KeyboardButton(text="Каталог", web_app=webAppTest) #создаем кнопку типа webapp
    keyboard.row(button) #добавляем кнопки в клавиатуру

    print(requests.get(f'{url}/categories/').json())
    buttons = []
    for category in requests.get(f'{url}/categories/').json():
        webAppTest = types.WebAppInfo(f"{url}/?user_id={user_id}&category={category['id']}") #создаем webappinfo - формат хранения url
        button = types.KeyboardButton(text=category['name'], web_app=webAppTest) #создаем кнопку типа webapp
        buttons.append(button)
    buttons_ = tuple(buttons)
    keyboard.add(*buttons_) #добавляем кнопки в клавиатуру


    return keyboard

def ChooseSize(item_id, sizes):
    inline_keyboard = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton(text="❌", callback_data=json.dumps({"item_id": item_id, "item_do":"__remove__"}))]

    for el in sizes:
        buttons.append(InlineKeyboardButton(text=el, callback_data=json.dumps({"item_id": item_id, "size":el})))

    inline_keyboard.row(*buttons)

    return inline_keyboard


def Confirm(user_id):
    inline_keyboard = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton(text="✅", callback_data=json.dumps({"user_id": user_id, "user_do": "confirm"})), InlineKeyboardButton(text="❌", callback_data=json.dumps({"user_id": user_id, "user_do": "deny"}))]

    inline_keyboard.row(*buttons)

    return inline_keyboard


def cart_to_text(user_id):
    cart = requests.get(f'{url}/users/{user_id}/cart/').json()
    msg = ""
    amount = 0
    for el in cart['cart']['items']:
        product_id = el['product_id']
        product = requests.get(f'{url}/products/{product_id}').json()
        msg += product["name"] + "(" + str(el['size']) + ") - " + str(product["price"]) + "р\n"
        amount += product["price"] 
    msg+=f"\nИтого: {amount}"

    return msg


@bot.callback_query_handler(func=lambda call: 'user_id' in call.data)
def button_callback_handler(call):
    data = json.loads(call.data)
    user_id = data['user_id']

    if data['user_do'] == 'confirm':
        requests.delete(f'{url}/users/{ call.message.chat.id }/cart/').json()
        bot.send_message(call.message.chat.id, f"Успешно! С вами свяжется администратор.")
        bot.edit_message_text(f"Подтверждено✅", call.message.chat.id, call.message.id)

        #TODO

    if data['user_do'] == 'deny':
        requests.delete(f'{url}/users/{ call.message.chat.id }/cart/').json()
        bot.send_message(call.message.chat.id, f"Ок. Корзина очищена.")
        bot.edit_message_text(f"Отменено❌", call.message.chat.id, call.message.id)

    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(func=lambda call: 'item_id' in call.data)
def button_callback_handler(call):
    data = json.loads(call.data)
    item_id = data['item_id']

    product_id = requests.get(f'{url}/items/{item_id}').json()['item']['product_id']
    product = requests.get(f'{url}/products/{product_id}').json()
    product_name = product['name']

    if 'item_do' in data and data['item_do'] == '__remove__':
        requests.delete(f'{url}/items/{item_id}').json()
        bot.edit_message_text(f"Удалено:\n{product_name}", call.message.chat.id, call.message.id)
        return

    size = data['size']

    requests.put(f'{url}/items/{item_id}/size/{size}').json()
    bot.edit_message_text(f"{product_name}\n\nВыбран размер: {size}", call.message.chat.id, call.message.id)

    cart = requests.get(f'{url}/users/{call.message.chat.id}/cart/').json()
    print(cart)
    for el in cart['cart']['items']:
        print(el)
        if el['size'] is None:
            bot.answer_callback_query(callback_query_id=call.id)
            return
        
    bot.send_message(call.message.chat.id, f"Успешно! Ваш заказ:")
    bot.send_message(call.message.chat.id, f"{cart_to_text(call.message.chat.id)}")
    bot.send_message(call.message.chat.id, f"Подтверждаете правильность заказа?", reply_markup=Confirm(call.message.chat.id))

    bot.answer_callback_query(callback_query_id=call.id)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print(message.from_user.id)
    bot.reply_to(message, "Приветствуем вас! Нажмите на одну из кнопок⬇", reply_markup=webAppKeyboard(message.from_user.id))


@bot.message_handler(commands=['id'])
def send_welcome(message):
    print(message.from_user.id)
    bot.reply_to(message, f"{message.from_user.id}")


@bot.message_handler(content_types="web_app_data")  # получаем отправленные данные
def answer(webAppMes):
    data = json.loads(webAppMes.web_app_data.data)
    msg = "Заказ:\n"
    amount = 0
    for el in data['cart']['items']:
        product_id = el['product_id']
        product = requests.get(f'{url}/products/{product_id}').json()
        print(product)
        bot.send_message(webAppMes.chat.id, product['name'], reply_markup=ChooseSize(el["id"], product['sizes']))

        product_name = product['name']
        product_price = product['price']
        msg += f"{ product_name } { product_price }р\n"
        amount += product_price


    msg += f"\nИтого: { amount }р"
    print(data)
    #product = requests.delete(f'{url}/users/{ webAppMes.chat.id }/cart/').json()
    #bot.send_message(webAppMes.chat.id, msg)
    #bot.send_message(webAppMes.chat.id, msg)


if __name__ == "__main__":
    bot.infinity_polling()
