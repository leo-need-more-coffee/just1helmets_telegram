import sys
sys.path.append('..')

import os

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import bs4
import json
import requests
import fsm

bot = telebot.TeleBot("6003211846:AAEjXt3qDu1df4zXEZT0OF41a0cCzyIBlYQ", parse_mode=None)

url = 'https://just1helmets-webapp.pzrnqt1vrss.xyz'
admins_id = [231843950, 524558139]


def is_state(chat_id, state_name):
    return state_name is None or (fsm.State.get(chat_id) and (state:=fsm.State.get(chat_id)).state == state_name)

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

def product_message(product_id):
    product = requests.get(f'{url}/products/{product_id}').json()
    name, description, price, sizes, image, category = product['name'], product['description'], product['price'], product['sizes'], product['image'], product['categories']
    sizes_ = ''.join([f'{el}, ' for el in sizes])[:-2]

    if len(description)-1 <= 200:
        description_ = description
    else:
        q=200
        while description[q] != ' ' and q>=0: 
            q-=1 
        description_ = description[:q] + '...'

    msg = f'Название: {name}\nОписание: {description_}\nЦена: {price}\nРазмеры: {sizes_}\nКатегория: {category} (список категорий /categories_list)'
    return msg, image

def admin(func):
    def inner(message):
        if message.chat.id in admins_id:
            func(message)
    return inner

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

def RequestContact():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    reg_button = types.KeyboardButton(text="Поделиться контактом", request_contact=True)
    keyboard.add(reg_button)
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

def EditProduct(product_id):
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(InlineKeyboardButton(text="Изменить название", callback_data=json.dumps({"product_id": product_id, "product_change": "name"})))
    inline_keyboard.add(InlineKeyboardButton(text="Изменить описание (максимум 400 символов)", callback_data=json.dumps({"product_id": product_id, "product_change": "description"})))
    inline_keyboard.add(InlineKeyboardButton(text="Изменить картинку (только ссылки)", callback_data=json.dumps({"product_id": product_id, "product_change": "image"})))
    inline_keyboard.add(InlineKeyboardButton(text='Изменить цену (только число, без "р")', callback_data=json.dumps({"product_id": product_id, "product_change": "price"})))
    inline_keyboard.add(InlineKeyboardButton(text="Изменить размеры (вводить без запятых через пробел)", callback_data=json.dumps({"product_id": product_id, "product_change": "sizes"})))
    inline_keyboard.add(InlineKeyboardButton(text="Изменить категорию (вводить номер категории, не название)", callback_data=json.dumps({"product_id": product_id, "product_change": "categories"})))
    inline_keyboard.add(InlineKeyboardButton(text="❌Удалить товар❌", callback_data=json.dumps({"product_id": product_id, "product_delete": True})))

    return inline_keyboard


@bot.message_handler(func=lambda message: is_state(message.chat.id, 'request_contact'), content_types=['contact'])
def contact_handler(message):
    print(message)
    msg = bot.send_message(231843950, f"Новый заказ:\n{cart_to_text(message.chat.id)}")
    bot.send_contact(231843950, **message.json()['contact'])

    fsm.State.delete(message.chat.id)

    requests.delete(f'{url}/users/{ message.chat.id }/cart/').json()

    bot.reply_to(message, "Успешно! С вами свяжется администратор.", reply_markup=webAppKeyboard(message.from_user.id))



@bot.message_handler(func=lambda message: is_state(message.chat.id, 'request_contact'))
def contact_handler(message):
    bot.reply_to(message, 'Пожалуйста, нажмите кнопку "Поделиться контактом"', reply_markup=RequestContact())


@bot.callback_query_handler(func=lambda call: 'product_delete' in call.data)
def button_callback_handler(call):
    data = json.loads(call.data)
    product_id = data['product_id']

    requests.delete(f'{url}/products/{product_id}')
    bot.edit_message_caption(caption=f'[ТОВАР УДАЛЕН]\n\n{call.message.caption}', chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=EditProduct(product_id))
    bot.send_message(call.message.chat.id, f"Товар удален.")


@bot.callback_query_handler(func=lambda call: 'product_change' in call.data)
def button_callback_handler(call):
    data = json.loads(call.data)
    fsm.State.set(call.message.chat.id, 'product_change', {'product_change': data['product_change'],'product_id': data['product_id'], 'message_id': call.message.id})
    bot.send_message(call.message.chat.id, f"Вводите:")

@bot.message_handler(func=lambda message: is_state(message.chat.id, 'product_change'))
def send_welcome(message):
    state = fsm.State.get(message.chat.id)
    data = state.data

    product_id = data['product_id']
    product = requests.get(f'{url}/products/{product_id}').json()
    if data['product_change'] == 'sizes':
        product[data['product_change']] =list(message.text.split())
    else:
        product[data['product_change']] = message.text
    requests.put(f'{url}/products', json=product)

    state.delete()

    product = requests.get(f'{url}/products/{product_id}').json()
    msg, image = product_message(product_id)
    if data['product_change'] != 'image':
        bot.edit_message_caption(caption=msg, chat_id=message.chat.id, message_id=data['message_id'], reply_markup=EditProduct(product_id))
        bot.send_message(message.chat.id, f"Успешно!")
    else:
        bot.edit_message_media(media=telebot.types.InputMediaPhoto(image, caption=msg), chat_id=message.chat.id, message_id=data['message_id'], reply_markup=EditProduct(product_id))
        bot.send_message(message.chat.id, f"Успешно!")

def ProductList(page=0, count=10):
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    products = requests.get(f'{url}/products/?page={page}&count={count}').json()
    max_page = ((l:=int(p:=(len(products)/count))) + int(p!=l))
    for product in products:
        inline_keyboard.add(InlineKeyboardButton(text=product['name'], callback_data=json.dumps({"product_id": product['id'], "do": "open_full"})))
    page_buttons = []
    if page > 0:
        page_buttons.append(InlineKeyboardButton(text='Предыдущая страница ⬅️', callback_data=json.dumps({"product_list_page": page-1, "count": count})))
    if page < max_page:
        page_buttons.append(InlineKeyboardButton(text='➡️ Следующая страница', callback_data=json.dumps({"product_list_page": page+1, "count": count})))
    inline_keyboard.row(*page_buttons)

    return inline_keyboard


@bot.callback_query_handler(func=lambda call: 'product_list_page' in call.data)
def button_callback_handler(call):
    data = json.loads(call.data)
    page = data['product_list_page']
    bot.edit_message_text(f"Каталог. Страница {page + 1}:", call.message.chat.id, call.message.id, reply_markup=ProductList(page, count=data['count']))
    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(func=lambda call: 'product_id' in call.data)
def button_callback_handler(call):
    data = json.loads(call.data)
    product_id = data['product_id']
    msg, image = product_message(product_id)

    bot.send_photo(call.message.chat.id, image, caption=msg, reply_markup=EditProduct(product_id))
    bot.answer_callback_query(callback_query_id=call.id)




@bot.callback_query_handler(func=lambda call: 'user_id' in call.data)
def button_callback_handler(call):
    data = json.loads(call.data)
    user_id = data['user_id']

    if data['user_do'] == 'confirm':
        bot.send_message(call.message.chat.id, f"Успешно! Пожалуйста, отправьте ваш контакт, чтобы с вами мог связаться наш администратор.", reply_markup=RequestContact())
        bot.edit_message_text(f"Подтверждено✅", call.message.chat.id, call.message.id)

        fsm.State.set(call.message.chat.id, 'request_contact')

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


@bot.message_handler(commands=['products'])
def send_welcome(message):
    bot.reply_to(message, "Каталог. Страница 1:", reply_markup=ProductList())

@bot.message_handler(commands=['categories_list'])
def send_welcome(message):
    categories = requests.get(f'{url}/categories/').json()
    msg = ""
    for i, category in enumerate(categories):
        name = category['name']
        msg += f'{i} - {name}\n'
    bot.reply_to(message, msg)


@bot.message_handler(commands=['add_product'])
def send_welcome(message):
    data = {
        "name": "ИМЯ ТОВАРА",
        "description": "ОПИСАНИЕ ",
        "image": "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.u2GosUQwlXG2QbkJopudIQHaE6%26pid%3DApi&f=1&ipt=524401fdcdda55a13f62bf577113e6569f3e3adca94055009a190c9662625985&ipo=images",
        "price": 0,
        "categories": 0,
        "sizes": []
    }
    product = requests.post(f'{url}/products', json=data).json()
    msg, image = product_message(product['id'])
    bot.send_photo(message.chat.id, image, caption=msg, reply_markup=EditProduct(product['id']))

if __name__ == "__main__":
    bot.infinity_polling()
