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

sell_skip = [
    [InlineKeyboardButton("💻ПК", callback_data='sell_skip_skip')],
    [InlineKeyboardButton("🖥️Товары для компьютера", callback_data='sell_skip_skip')],
    [InlineKeyboardButton("🛠️Комплектующие для компьютера", callback_data='sell_skip_skip')],
    [InlineKeyboardButton("🖧Серверное оборудование", callback_data='sell_skip_skip')],
    [InlineKeyboardButton("🌐Сетевое оборудование", callback_data='sell_skip_skip')],
    [InlineKeyboardButton("🖨️Офисная техника и расходники", callback_data='sell_skip_skip')],
    [InlineKeyboardButton("📱Телефоны", callback_data='sell_skip_skip')],
    [InlineKeyboardButton("💿Программное обеспечение", callback_data='sell_skip_skip')],
    [InlineKeyboardButton("🔙Назад", callback_data='sell')],

]
sell_skip_markup = InlineKeyboardMarkup(sell_skip)
sell_skip_pod = [
    [InlineKeyboardButton("🖥️Стационарные ПК", callback_data='sell_skip')],
    [InlineKeyboardButton("💻Ноутбуки", callback_data='sell_skip')],
    [InlineKeyboardButton("🖨️Моноблоки", callback_data='sell_skip')],
    [InlineKeyboardButton("📱Планшеты", callback_data='sell_skip')],
    [InlineKeyboardButton("🔙Назад", callback_data='sell_skip')],
]
sell_skip_pod_markup = InlineKeyboardMarkup(sell_skip_pod)
text_category="🔍Выберите категорию вашего товара."

text_sell="📸 Пожалуйста, отправьте фото. Не более 10 штук."
sell = [[InlineKeyboardButton("➡️Пропустить", callback_data='sell_skip')],
        [InlineKeyboardButton("🔙Назад", callback_data='nazad')]]
sell_markup = InlineKeyboardMarkup(sell)
saved_photo = None
skip_catergory=None
skip_pod_category=None
skip_pod_pod_category=None

def process_message(json_data):
    global saved_photo
    chat_id = json_data['message']['chat']['id']
    message_text = json_data['message'].get('text', "")
    chat_username = json_data['message']['chat'].get('username', 'username')

    if 'reply_to_message' in json_data['message']:
        reply_chat_id = json_data['message']['reply_to_message']['chat'].get('id', None)
        reply_message=json_data['message']['reply_to_message']['text']

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

        bot.send_message(group_id, text=support)

    elif user_states.get(chat_id) == "awaiting_photo":
        if 'photo' in json_data['message']:
            photo = json_data['message']['photo'][-1]  # Get the highest resolution
            saved_photo = photo['file_id']

            bot.send_message(
                chat_id,
                text=text_category,
                reply_markup=sell_skip_markup
            )




    else:

        if message_text == '/start':
            text = (f"✨ Привет! Этот бот создан для удобной и быстрой публикации "
                    f"объявлений на канале @ITbarakholka. 🚀 Рад приветствовать тебя, @{chat_username}!")
            bot.send_message(chat_id, text, reply_markup=inline_markup)

user_selected_category = {}
def generate_category_keyboard(chat_id):
    categories = [
        ("ПК", 'pc'),
        ("Товары для компьютера", 'pc_comp'),
        ("Комплектующие для компьютера", 'pc_comp1'),
        ("Сетевое оборудование", 'pc_network'),
        ("Офисная техника и расходники", 'pc_office'),
        ("Телефоны", 'pc_phone'),
        ("Программное обеспечение", 'pf_software'),
    ]

    continue_key = []

    # Loop through all categories and mark the selected category with ✅
    for category_name, callback_value in categories:
        # If the category is selected, add a ✅ next to it
        if user_selected_category.get(chat_id) == callback_value:
            category_button = InlineKeyboardButton(f"✅ {category_name}", callback_data=callback_value)
        else:
            category_button = InlineKeyboardButton(category_name, callback_data=callback_value)

        continue_key.append([category_button])

    # Add buttons for "Продолжить", "Искать", and "Назад"
    continue_key.extend([
        [InlineKeyboardButton("➡️Продолжить", callback_data='pc_continue')],
        [InlineKeyboardButton("🔍Искать", callback_data='pc_search')],
        [InlineKeyboardButton("🔙Назад", callback_data='nazad')],
    ])

    return InlineKeyboardMarkup(continue_key)


def process_callback_query(json_data):
    query = json_data['callback_query']
    chat_id = query['message']['chat']['id']
    message_id=query['message']['message_id']

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

        user_states[chat_id] = 'awaiting_ad_text'


    elif callback_data_message == "support":
        bot.send_message(chat_id,text="💬 Здесь вы можете задать вопрос нашей поддержке. Напишите Ваше сообщение в чат, и мы ответим Вам в ближайшее время!",reply_markup=nazad_markup)
        user_states[chat_id] = 'awaiting_support_text'

    elif callback_data_message == "nazad":

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Меню:"  # Update the message text
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=query['message']['message_id'],
            reply_markup=inline_markup
        )

    elif callback_data_message == "pc_continue":

        pc_continue = [
            [InlineKeyboardButton("Стационарные ПК", callback_data='pc_desktop')],
            [InlineKeyboardButton("Ноутбуки", callback_data='pc_laptop')],
            [InlineKeyboardButton("Моноблоки", callback_data='pc_desktop')],
            [InlineKeyboardButton("Планшеты", callback_data='pc_monoblock')],
            [InlineKeyboardButton("➡️Продолжить", callback_data='pc_post')],
            [InlineKeyboardButton("🔍Искать", callback_data='pc_search')],
            [InlineKeyboardButton("🔙Назад", callback_data='category')],

        ]
        pc_continue_markup = InlineKeyboardMarkup(pc_continue)

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔽 Выберите подкатегорию, отмечая её галочкой ✅. Или же, можете пропустить этот шаг и просто нажать «➡️Продолжить» ."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=query['message']['message_id'],
            reply_markup=pc_continue_markup
        )




    elif callback_data_message == "category":
        text="🔍 Выберите категорию для поиска объявлений. Вы можете отметить несколько вариантов, отметив их кнопкой ✅   Чтобы перейти дальше, нажмите «➡️Продолжить»."
        continue_markup = generate_category_keyboard(chat_id)

        # Edit the message with updated text and keyboard
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=continue_markup
        )
    elif callback_data_message == 'sell':


        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text_sell
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=sell_markup
        )
        user_states[chat_id] = 'awaiting_photo'

    elif callback_data_message == 'sell_skip':
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text_category
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=sell_skip_markup
        )
    elif callback_data_message == 'sell_skip_skip':
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подкатегорию вашего товара"
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=sell_skip_pod_markup
        )










def index(request):
    return HttpResponse("Hello, World!")

