from django.http import HttpResponse
from django.shortcuts import render
import json
import telegram
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton,WebAppInfo
group_id=-4587708639
user_states = {}
bot = telegram.Bot("7677882278:AAHiw2W0wxkrBZmJEj12DwQryxgR3qucWZ4")
@csrf_exempt
@require_POST
def webhook(request):
    if request.method == 'POST':
        json_data = json.loads(request.body.decode('utf-8'))
        if 'message' in json_data:
            process_message(json_data)
        elif 'callback_query' in json_data:
            process_callback_query(json_data)

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)

inline_keyboard = [
            [InlineKeyboardButton("💰 Продажа", callback_data='sell'),
             InlineKeyboardButton("🛒 Покупка", callback_data='buy')],
            [InlineKeyboardButton("📋 Мои объявления", callback_data='posts')],
            [InlineKeyboardButton("🔍 Поиск по категориям", callback_data='category')],
            [InlineKeyboardButton("🛠️ Поддержка", callback_data='support')],
            [InlineKeyboardButton("📢 Купить рекламу", callback_data='ads')],
        ]
inline_markup = InlineKeyboardMarkup(inline_keyboard)
def process_message(json_data):
    chat_id = json_data['message']['chat']['id']
    message_text = json_data['message'].get('text', "")
    chat_username = json_data['message']['chat'].get('username', 'username')

    if 'reply_to_message' in json_data['message']:
        reply_chat_id = json_data['message']['reply_to_message']['chat'].get('id', None)
        reply_message=json_data['message']['reply_to_message']['text']
        #from_chat=json_data['message']['from']['id']
        if reply_chat_id == group_id:

            user_id = re.search(r'id:(\d+)', reply_message).group(1)
            end = [[InlineKeyboardButton("❌Закончить диалог", callback_data='nazad')]]
            end_markup = InlineKeyboardMarkup(end)
            bot.send_message(user_id,text=f'Ответ от поддержки: {message_text}', reply_markup=end_markup)

    # Check if the user is in "ads" state
    if user_states.get(chat_id) == 'awaiting_ad_text':

        user_states.pop(chat_id)
        ads = (f"📢 Новая заявка на размещение рекламы! Текст рекламы: {message_text} "
               f"💬 Свяжитесь с пользователем @{chat_username} для уточнения деталей")
        bot.send_message(group_id, text=ads)
        bot.send_message(chat_id, text="✅ Ваша реклама успешно отправлена! Ожидайте, администратор свяжется с вами для уточнения деталей.")

    elif user_states.get(chat_id) == 'awaiting_support_text':

        user_states.pop(chat_id)
        support = f"Пользователь @{chat_username} id:{chat_id} написал: {message_text}"
        #support = f"Пользователь @{chat_username} id:{chat_id}  написал: {message_text}"


        bot.send_message(group_id, text=support)

    else:

        if message_text == '/start':
            text = (f"✨ Привет! Этот бот создан для удобной и быстрой публикации "
                    f"объявлений на канале @ITbarakholka. 🚀 Рад приветствовать тебя, @{chat_username}!")
            bot.send_message(chat_id, text, reply_markup=inline_markup)

def process_callback_query(json_data):
    query = json_data['callback_query']
    chat_id = query['message']['chat']['id']
    callback_data_message = query['data']
    nazad_key = [[InlineKeyboardButton("🔙Назад", callback_data='nazad')]]
    nazad_markup = InlineKeyboardMarkup(nazad_key)

    if callback_data_message == "ads":
        bot.send_message(
            chat_id,
            text="📢 Вы можете разместить свою рекламу на нашем канале и в боте! "
                 "Пожалуйста, введите текст вашей рекламы. После отправки ваша заявка будет обработана, и администратор свяжется с вами!",
            reply_markup=nazad_markup
        )
        # Set user state to "awaiting_ad_text"
        user_states[chat_id] = 'awaiting_ad_text'


    elif callback_data_message == "support":
        bot.send_message(chat_id,text="💬 Здесь вы можете задать вопрос нашей поддержке. Напишите Ваше сообщение в чат, и мы ответим Вам в ближайшее время!",reply_markup=nazad_markup)
        user_states[chat_id] = 'awaiting_support_text'

    elif callback_data_message == "nazad":
        # Return to the main menu
        bot.send_message(chat_id, text="Меню:", reply_markup=inline_markup)

def index(request):
    return HttpResponse("Hello, World!")

