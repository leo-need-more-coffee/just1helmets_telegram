import os
import sys
sys.path.append('./webapp')
sys.path.append('./bot')


import telebot
from webapp import app as application
from bot import bot

if __name__ == '__main__':
    bot.infinity_polling()

