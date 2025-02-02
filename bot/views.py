from django.http import HttpResponse
from datetime import date
import random
import string
from django.shortcuts import render
import json
import telegram
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import re
from telegram.utils.request import Request
from .models import Posts, Telegram_users, statics
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, \
    InputMediaPhoto
from config import TOKEN_BOT, CHANEL_ADS, CHANEL_MAIN, CHANEL_SUPPORT, ADMIN

main_id = CHANEL_MAIN
group_id = CHANEL_SUPPORT
ads_id = CHANEL_ADS
admin = ADMIN
# print(admin)
user_states = {}
user_photo = {}
user_text = {}
user_message_id = {}

request = Request(connect_timeout=35, read_timeout=35)
bot = telegram.Bot(TOKEN_BOT, request=request)


def add_b_tags(text, username='username', chat_id='1'):
    if username == None:
        username = 'username'
    labels = [
        "Тип", "Категория", "Подкатегория", "Пользователь", "Описание",
        "Контакты", "Цена", "Город", "Автор", "Отправлено через", 'Айди'
    ]

    for label in labels:
        text = text.replace(f"{label}:", f"<b>{label}:</b>")

    mention_text = f'<a href="tg://user?id={chat_id}">{username}</a>'
    text = text.replace(f'{username}', mention_text)

    return text


@csrf_exempt
@require_POST
def webhook(request):
    if request.method == 'POST':
        json_data = json.loads(request.body.decode('utf-8'))

        # Extract the user ID from the incoming message (if present)
        user_id = None
        if 'message' in json_data:
            user_id = json_data['message']['from']['id']
        elif 'callback_query' in json_data:
            user_id = json_data['callback_query']['from']['id']

        # Check if the user is in the blocked users list
        if user_id and Telegram_users.objects.filter(user_id=user_id, block=True).exists():
            # Optionally log or send a response to indicate user is blocked
            return HttpResponse("User is blocked", status=200)  # Forbidden status

        # Proceed with processing if user is not blocked
        if 'message' in json_data:
            process_message(json_data)
        elif 'callback_query' in json_data:
            process_callback_query(json_data)

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)


admin_keyboard = [
    [InlineKeyboardButton("🚀Рассылка", callback_data='admin_ads')],
    [InlineKeyboardButton("📊Статистика", callback_data='statics')],
    [InlineKeyboardButton("🚫Блокировка/разблокировка", callback_data='ban')]
]
admin_keyboard_markup = InlineKeyboardMarkup(admin_keyboard)
top_category = [
    [InlineKeyboardButton("💰 Продажа", callback_data='category#sell')],
    [InlineKeyboardButton("🛒 Покупка", callback_data='category#buy')],
    [InlineKeyboardButton("Все", callback_data='category#all')],
    [InlineKeyboardButton("🔙Назад", callback_data='nazad')]
]
top_category_markup = InlineKeyboardMarkup(top_category)
admin_menu_text = "👋Добро пожаловать в административную панель."

statics_nazad = [[InlineKeyboardButton("🔙Назад", callback_data='statics_nazad')]]
statics_nazad_markup = InlineKeyboardMarkup(statics_nazad)

block_or_unblock = [[InlineKeyboardButton("🔙Меню", callback_data='statics_nazad')]]
block_or_unblock_markup = InlineKeyboardMarkup(block_or_unblock)

# inline_keyboard = [
#             [InlineKeyboardButton("💰 Продажа", callback_data='sell'),
#              InlineKeyboardButton("🛒 Покупка", callback_data='buy')],
#             [InlineKeyboardButton("📋 Мои объявления", callback_data='posts')],
#             [InlineKeyboardButton("🔍 Поиск по категориям", callback_data='category')],
#             [InlineKeyboardButton("🛠️ Поддержка", callback_data='support')],
#             [InlineKeyboardButton("📢 Купить рекламу", callback_data='ads')],
#         ]
# inline_markup = InlineKeyboardMarkup(inline_keyboard)
reply_keyboard = [
    [KeyboardButton("💰 Продажа"), KeyboardButton("🛒 Покупка")],
    [KeyboardButton("📋 Мои объявления")],
    [KeyboardButton("🔍 Поиск по категориям")],
    [KeyboardButton("🛠️ Поддержка")],
    [KeyboardButton("📢 Купить рекламу")]
]
markup_reply = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

sell_skip = [
    [InlineKeyboardButton("💻ПК", callback_data='pk#ПК')],
    [InlineKeyboardButton("🖥️Товары для компьютера", callback_data='items#Товары_для_компьютера')],
    [InlineKeyboardButton("🛠️Комплектующие для компьютера", callback_data='cat#Комплектующие_для_компьютера')],
    [InlineKeyboardButton("🖧Серверное оборудование", callback_data='server#Серверное_оборудование')],
    [InlineKeyboardButton("🌐Сетевое оборудование", callback_data='cat#Сетевое_оборудование')],
    [InlineKeyboardButton("🖨️Офисная техника и расходники", callback_data='cat#Офисная_техника_и_расходники')],
    [InlineKeyboardButton("📱Телефоны", callback_data='cat#Телефоны')],
    [InlineKeyboardButton("💿Программное обеспечение", callback_data='cat#Программное_обеспечение')],
    [InlineKeyboardButton("🔙Назад", callback_data='sell')],

]
sell_skip_markup = InlineKeyboardMarkup(sell_skip)
pk_cat_inline=[
    [InlineKeyboardButton("🖥️Стационарные ПК", callback_data='personalpc#Стационарные_ПК')],
    [InlineKeyboardButton("💻Ноутбуки", callback_data='nout#Ноутбуки')],
    [InlineKeyboardButton("🖨️Моноблоки", callback_data='monoblock#Моноблоки')],
    [InlineKeyboardButton("📱Планшеты", callback_data='planshet#Планшеты')],
    [InlineKeyboardButton("🔙Назад", callback_data='sell_skip')],
]
pk_cat_inline_markup=InlineKeyboardMarkup(pk_cat_inline)
items_cat_inline=[
    [InlineKeyboardButton("Мониторы", callback_data='monitor#Мониторы')],
    [InlineKeyboardButton("Клавиатуры_и_мыши", callback_data='keyboard#Клавиатуры_и_мыши')],
    [InlineKeyboardButton("Акссесуары", callback_data='aksessuar#Акссесуары')],
    [InlineKeyboardButton("🔙Назад", callback_data='sell_skip')],
]
items_cat_inline_markup=InlineKeyboardMarkup(items_cat_inline)

server_cat_inline=[
    [InlineKeyboardButton("Серверы", callback_data='switch#Серверы')],
    [InlineKeyboardButton("Жёсткие_диски", callback_data='hard#Жёсткие_диски')],
    [InlineKeyboardButton("Процессоры", callback_data='processor#Процессоры')],
    [InlineKeyboardButton("🔙Назад", callback_data='sell_skip')],
]
server_cat_inline_markup=InlineKeyboardMarkup(server_cat_inline)


sell_skip_pod = [
    [InlineKeyboardButton("🖥️Стационарные ПК", callback_data='pod#Стационарные_ПК')],
    [InlineKeyboardButton("💻Ноутбуки", callback_data='pod#Ноутбуки')],
    [InlineKeyboardButton("🖨️Моноблоки", callback_data='pod#Моноблоки')],
    [InlineKeyboardButton("📱Планшеты", callback_data='pod#Планшеты')],
    [InlineKeyboardButton("🔙Назад", callback_data='sell_skip')],
]
sell_skip_pod_markup = InlineKeyboardMarkup(sell_skip_pod)

pk_pod_pod=[
    [InlineKeyboardButton("msi_pk", callback_data='skip#msi_pk')],
    [InlineKeyboardButton("hp_pk", callback_data='skip#hp_pk')],
    [InlineKeyboardButton("lenovo_pk", callback_data='skip#lenovo_pk')],
    [InlineKeyboardButton("➡️Пропустить", callback_data='skip')],
    [InlineKeyboardButton("🔙Назад", callback_data='pk')],
]
pk_pod_pod_markup=InlineKeyboardMarkup(pk_pod_pod)
laptop_pod_pod=[
    [InlineKeyboardButton("msi_nout", callback_data='skip#msi_nout')],
    [InlineKeyboardButton("hp_nout", callback_data='skip#hp_nout')],
    [InlineKeyboardButton("lenovo_nout", callback_data='skip#lenovo_nout')],
    [InlineKeyboardButton("➡️Пропустить", callback_data='skip')],
    [InlineKeyboardButton("🔙Назад", callback_data='pk')],
]
laptop_pod_pod_markup=InlineKeyboardMarkup(laptop_pod_pod)
monoblock_pod_pod=[
    [InlineKeyboardButton("msi_monoblok", callback_data='skip#msi_monoblok')],
    [InlineKeyboardButton("hp_monoblok", callback_data='skip#hp_monoblok')],
    [InlineKeyboardButton("lenovo_monoblok", callback_data='skip#lenovo_monoblok')],
    [InlineKeyboardButton("➡️Пропустить", callback_data='skip')],
    [InlineKeyboardButton("🔙Назад", callback_data='pk')],
]
monoblock_pod_pod_markup=InlineKeyboardMarkup(monoblock_pod_pod)
planshet_pod_pod=[
    [InlineKeyboardButton("msi_planshet", callback_data='skip#msi_planshet')],
    [InlineKeyboardButton("hp_planshet", callback_data='skip#hp_planshet')],
    [InlineKeyboardButton("lenovo_planshet", callback_data='skip#lenovo_planshet')],
    [InlineKeyboardButton("➡️Пропустить", callback_data='skip')],
    [InlineKeyboardButton("🔙Назад", callback_data='pk')],
]
planshet_pod_pod_markup=InlineKeyboardMarkup(planshet_pod_pod)

#############################
monitor_pod_pod=[
    [InlineKeyboardButton("msi_monitor", callback_data='skip#msi_monitor')],
    [InlineKeyboardButton("hp_monitor", callback_data='skip#hp_monitor')],
    [InlineKeyboardButton("lenovo_monitor", callback_data='skip#lenovo_monitor')],
    [InlineKeyboardButton("➡️Пропустить", callback_data='skip')],
    [InlineKeyboardButton("🔙Назад", callback_data='items')],
]
monitor_pod_pod_markup=InlineKeyboardMarkup(monitor_pod_pod)
keyboard_pod_pod=[
    [InlineKeyboardButton("msi_klava", callback_data='skip#msi_klava')],
    [InlineKeyboardButton("hp_klava", callback_data='skip#hp_klava')],
    [InlineKeyboardButton("lenovo_klava", callback_data='skip#lenovo_klava')],
    [InlineKeyboardButton("➡️Пропустить", callback_data='skip')],
    [InlineKeyboardButton("🔙Назад", callback_data='items')],
]
keyboard_pod_pod_markup=InlineKeyboardMarkup(keyboard_pod_pod)
aksessuar_pod_pod=[
    [InlineKeyboardButton("msi_acses", callback_data='skip#msi_acses')],
    [InlineKeyboardButton("hp_acses", callback_data='skip#hp_acses')],
    [InlineKeyboardButton("lenovo_acses", callback_data='skip#lenovo_acses')],
    [InlineKeyboardButton("➡️Пропустить", callback_data='skip')],
    [InlineKeyboardButton("🔙Назад", callback_data='items')],
]
aksessuar_pod_pod_markup=InlineKeyboardMarkup(aksessuar_pod_pod)

#######################################
server_pod_pod=[
    [InlineKeyboardButton("msi_server", callback_data='skip#msi_server')],
    [InlineKeyboardButton("hp_server", callback_data='skip#hp_server')],
    [InlineKeyboardButton("lenovo_server", callback_data='skip#lenovo_server')],
    [InlineKeyboardButton("➡️Пропустить", callback_data='skip')],
    [InlineKeyboardButton("🔙Назад", callback_data='server')],
]
server_pod_pod_markup=InlineKeyboardMarkup(server_pod_pod)
hard_pod_pod=[
    [InlineKeyboardButton("msi_hdd", callback_data='skip#msi_hdd')],
    [InlineKeyboardButton("hp_hdd", callback_data='skip#hp_hdd')],
    [InlineKeyboardButton("lenovo_hdd", callback_data='skip#lenovo_hdd')],
    [InlineKeyboardButton("➡️Пропустить", callback_data='skip')],
    [InlineKeyboardButton("🔙Назад", callback_data='server')],
]
hard_pod_pod_markup=InlineKeyboardMarkup(hard_pod_pod)
proccessor_pod_pod=[
    [InlineKeyboardButton("msi_proc", callback_data='skip#msi_proc')],
    [InlineKeyboardButton("hp_proc", callback_data='skip#hp_proc')],
    [InlineKeyboardButton("lenovo_proc", callback_data='skip#lenovo_proc')],
    [InlineKeyboardButton("➡️Пропустить", callback_data='skip')],
    [InlineKeyboardButton("🔙Назад", callback_data='server')],
]
proccessor_pod_pod_markup=InlineKeyboardMarkup(proccessor_pod_pod)



















#####################################
sell_skip_pod_category = [
    [InlineKeyboardButton("🤖Android", callback_data='skip#android')],
    [InlineKeyboardButton("🍎Apple", callback_data='skip#apple')],
    [InlineKeyboardButton("➡️Пропустить", callback_data='skip')],
    [InlineKeyboardButton("🔙Назад", callback_data='cat')],
]
sell_skip_pod_category_markup = InlineKeyboardMarkup(sell_skip_pod_category)

##############################################################################

search_pod_pc=[
    [InlineKeyboardButton("Стационарные_ПК", callback_data='#')],
    [InlineKeyboardButton("Ноутбуки", callback_data='#')],
    [InlineKeyboardButton("Моноблоки", callback_data='#')],
    [InlineKeyboardButton("Планшеты", callback_data='#')],
]
search_pod_items=[
    [InlineKeyboardButton("Мониторы", callback_data='#')],
    [InlineKeyboardButton("Клавиатуры_и_мыши", callback_data='#')],
    [InlineKeyboardButton("Акссесуары", callback_data='#')],
    [InlineKeyboardButton("Планшеты", callback_data='#')],
]
search_pod_server=[
    [InlineKeyboardButton("Серверы", callback_data='#')],
    [InlineKeyboardButton("Жёсткие_диски", callback_data='#')],
    [InlineKeyboardButton("Процессоры ", callback_data='#')],
]
text_category = "🔍Выберите категорию вашего товара."

text_sell = "📸 Пожалуйста, отправьте фото. Не более 10 штук."
sell = [[InlineKeyboardButton("➡️Пропустить", callback_data='sell_skip')],
        [InlineKeyboardButton("🔙Назад", callback_data='nazad')]]
sell_markup = InlineKeyboardMarkup(sell)

nazad_description = [[InlineKeyboardButton("🔙Назад", callback_data='pod')]]
nazad_description_markup = InlineKeyboardMarkup(nazad_description)
awaiting_description = [[InlineKeyboardButton("🔙Назад", callback_data='awaiting_description')]]
awaiting_description_markup = InlineKeyboardMarkup(awaiting_description)
awaiting_price = [[InlineKeyboardButton("🔙Назад", callback_data='awaiting_price')]]
awaiting_price_markup = InlineKeyboardMarkup(awaiting_price)
awaiting_city = [[InlineKeyboardButton("🔙Назад", callback_data='awaiting_city')]]
awaiting_city_markup = InlineKeyboardMarkup(awaiting_city)
saved_photo = []
skip_catergory = None
skip_pod_category = None
skip_pod_pod_category = ""
price = None
phone = None
description = None
city = None
nazad_key = [[InlineKeyboardButton("🔙Назад", callback_data='nazad')]]
nazad_markup = InlineKeyboardMarkup(nazad_key)
bron = [[InlineKeyboardButton("📝Забронировать", callback_data='bron')]]
bron_markup = InlineKeyboardMarkup(bron)
call = None


def fetch_active(chat_id):
    active = 0
    fetch_profile = Telegram_users.objects.all()
    for item in fetch_profile:
        try:
            if chat_id == item.user_id:
                active += 1
            else:
                check = bot.send_message(chat_id=item.user_id, text=".")
                bot.delete_message(chat_id=item.user_id, message_id=check.message_id)
                active += 1


        except Exception as e:
            pass
    statics.objects.create(static=active)
    return active


def process_message(json_data):
    global saved_photo, price, description, city, phone, call, user_photo, user_text, user_message_id
    chat_id = json_data['message']['chat']['id']
    message_text = json_data['message'].get('text', "")
    message = json_data['message']
    chat_username = json_data['message']['chat'].get('username', 'username')
    chat_name = json_data['message']['chat'].get('first_name', 'first_name')

    if 'reply_to_message' in json_data['message']:
        reply_chat_id = json_data['message']['reply_to_message']['chat'].get('id', None)
        reply_message = json_data['message']['reply_to_message']['text']

        if reply_chat_id == ads_id:
            user_id = re.search(r'id:(\d+)', reply_message).group(1)
            end = [[InlineKeyboardButton("❌Закончить диалог", callback_data='nazad')]]
            end_markup = InlineKeyboardMarkup(end)
            bot.send_message(user_id, text=f'Ответ от поддержки: {message_text}', reply_markup=end_markup)
    if message_text == '/start':

        try:
            Telegram_users.objects.create(user_id=chat_id)

        except Exception as e:
            pass
            # print(e)
        mention_text = f"[{chat_username}](tg://user?id={chat_id})"
        text = (f"✨ Привет! Этот бот создан для удобной и быстрой публикации "
                f"объявлений на канале @ITbarakholka. 🚀 Рад приветствовать тебя, {mention_text}!")

        bot.send_message(chat_id, text, reply_markup=markup_reply, parse_mode="Markdown")  ##repl=markup_reply
    elif message_text == "💰 Продажа":
        saved_photo = []
        call = 'sell'

        bot.send_message(chat_id, text="📸 Пожалуйста, отправьте фото. Не более 10 штук.", reply_markup=nazad_markup)
        user_states[chat_id] = 'awaiting_photo'
    elif message_text == "🛒 Покупка":
        saved_photo = []
        call = 'buy'

        bot.send_message(chat_id, text="📸 Пожалуйста, отправьте фото. Не более 10 штук.", reply_markup=sell_markup)
        user_states[chat_id] = 'awaiting_photo'

    elif message_text == "📋 Мои объявления":
        try:
            post = Posts.objects.filter(user_id=chat_id)
            for item in post:
                delete_post = [[InlineKeyboardButton("❌Удалить", callback_data=f'delete_posts#{item.message_id}')]]
                delete_post_markup = InlineKeyboardMarkup(delete_post)
                if item.random_key:
                    media_group = [
                        InputMediaPhoto(media=file_id,
                                        caption=add_b_tags(item.caption, chat_username, chat_id) if i == 0 else None,
                                        parse_mode='HTML')
                        for i, file_id in enumerate(item.photo)
                    ]
                    messages = bot.send_media_group(
                        chat_id=item.user_id,
                        media=media_group,
                    )
                    bot.send_message(item.user_id, text='👆🏻Пост выше👆🏻', reply_markup=delete_post_markup)

                else:
                    bot.copy_message(item.user_id, from_chat_id=main_id, message_id=item.message_id,
                                     reply_markup=delete_post_markup)

                bot.send_message(item.user_id, text=f'Ссылка на пост:https://t.me/mainbarxolka/{item.message_id}',
                                 disable_web_page_preview=True)




        except Exception as e:
            pass


    elif message_text == "🔍 Поиск по категориям":
        text = "🔍 Выберите категорию для поиска объявлений"

        bot.send_message(chat_id, text=text, reply_markup=top_category_markup)
    elif message_text == "🛠️ Поддержка":

        bot.send_message(chat_id,
                         text="💬 Здесь вы можете задать вопрос нашей поддержке. Напишите Ваше сообщение в чат, и мы ответим Вам в ближайшее время!",
                         reply_markup=nazad_markup)
        user_states[chat_id] = 'awaiting_support_text'
    elif message_text == "📢 Купить рекламу":
        last_object = statics.objects.last()
        if last_object:
            static_value = last_object.static
        else:
            static_value = 0
        statics_chanel = bot.get_chat_member_count(main_id)
        text = f"📢 Вы можете разместить свою рекламу на нашем канале и в боте !\nТекущая статистика:  \n📊 Кол-во пользователей на канале: {statics_chanel} \n👥 Кол-во активных пользователей в боте: {static_value}   \n\nПожалуйста, введите текст вашей рекламы. После отправки ваша заявка будет обработана, и администратор свяжется с вами!"

        bot.send_message(chat_id, text=text, reply_markup=nazad_markup)
        user_states[chat_id] = 'awaiting_ad_text'





    elif message_text == '/admin':

        if int(chat_id) == int(admin):
            bot.send_message(chat_id, text=admin_menu_text, reply_markup=admin_keyboard_markup)
    elif message_text == '/users':
        if int(chat_id) == int(admin):
            today = Telegram_users.objects.filter(created_at__date=date.today()).count()
            all_users = Telegram_users.objects.all().count()
            bot.send_message(chat_id,
                             text=f'Всего пользователей в боте: {all_users} \nНовых пользователей за сутки: {today}')

    # Check if the user is in "ads" state

    # if saved_photo:
    #     bot.send_photo(chat_id,caption=text,photo=saved_photo,reply_markup=approve_markup)
    # else:
    #     bot.send_message(chat_id,text=text,reply_markup=approve_markup)

    else:
        if user_states.get(chat_id) == 'awaiting_ad_text':
            mention_text = f"[{chat_username}](tg://user?id={chat_id})"
            # mention_text = f"[{name}](tg://user?id={user})"

            ads = (f"📢 Новая заявка на размещение\nрекламы!\nТекст рекламы:\n{message_text} "
                   f"\n💬 Свяжитесь с пользователем\n {mention_text} для уточнения деталей")
            bot.send_message(ads_id, text=ads, parse_mode="Markdown")
            bot.send_message(chat_id,
                             text=f"✅ Ваша реклама успешно отправлена! Ожидайте, администратор свяжется с вами для уточнения деталей.")
            user_states.pop(chat_id)

        elif user_states.get(chat_id) == 'awaiting_support_text':
            mention_text = f"[{chat_username}](tg://user?id={chat_id})"
            support = f"Пользователь {mention_text} id:{chat_id} написал: {message_text}"
            bot.send_message(chat_id, text='📩Ваше сообщение отправлено, ждите ответ.', reply_markup=nazad_markup)

            bot.send_message(ads_id, text=support, parse_mode="Markdown")

        elif user_states.get(chat_id) == "awaiting_photo":
            # user_states.pop(chat_id)

            if 'photo' in json_data['message']:
                if 'media_group_id' in json_data['message']:

                    photo = json_data['message']['photo'][-1]
                    saved_photo.append(photo['file_id'])
                    if len(saved_photo) == 1:
                        bot.send_message(
                            chat_id,
                            text=text_category,
                            reply_markup=sell_skip_markup
                        )


                else:
                    user_states.pop(chat_id)
                    photo = json_data['message']['photo'][-1]
                    saved_photo.append(photo['file_id'])
                    bot.send_message(
                        chat_id,
                        text=text_category,
                        reply_markup=sell_skip_markup
                    )

                # media_group = [InputMediaPhoto(media=file_id) for file_id in saved_photo]
                # bot.send_media_group(chat_id=531080457, media=media_group)
                # print(saved_photo)



        elif user_states.get(chat_id) == 'awaiting_description':

            description = message_text
            bot.send_message(chat_id, text='📞 Отправьте свои контактные данные.',
                             reply_markup=awaiting_description_markup)
            user_states[chat_id] = 'awaiting_price'
        elif user_states.get(chat_id) == 'awaiting_price':

            phone = message_text
            bot.send_message(chat_id, text='💰 Укажите стоимость товара', reply_markup=awaiting_price_markup)
            user_states[chat_id] = 'awaiting_city'
        elif user_states.get(chat_id) == 'awaiting_city':

            price = message_text
            bot.send_message(chat_id,
                             text='🏙️ Укажите город одним словом или с нижним подчёркиванием.  Например: Санкт_Петербург. (Это нужно для формирования хэштега города, чтобы облегчить поиск).',
                             reply_markup=awaiting_city_markup)
            user_states[chat_id] = 'awaiting_complete'
        elif user_states.get(chat_id) == 'awaiting_complete':
            approve = [[InlineKeyboardButton("✅Опубликовать", callback_data=f'approve#{chat_id}')],
                       [InlineKeyboardButton("🔙Назад", callback_data='nazad')]]
            approve_markup = InlineKeyboardMarkup(approve)
            city = message_text
            user = Telegram_users.objects.filter(user_id=chat_id).first()

            text = (
                f"Тип: #{'Продажа' if call == 'sell' else 'Покупка'}\n\n"
                f"Категория: #{skip_catergory}\n"
                f"Подкатегория: #{skip_pod_category}\n"
                f"Подкатегория: #{skip_pod_pod_category}\n"
                f"Пользователь: #user{user.id}\n"
                f"Айди: {chat_id}\n\n"
                f"Описание: {description}\n\n"
                f"Контакты: {phone}\n"
                f"Цена: {price}\n"
                f"Город: #{city}\n"
                f"Автор: {chat_username}\n\n"
                f"Отправлено через: @ITbarakholka_bot"

            )

            if saved_photo:
                if len(saved_photo) == 1:
                    bot.send_photo(chat_id, caption=add_b_tags(text, chat_username, chat_id), photo=saved_photo[0],
                                   reply_markup=approve_markup,
                                   parse_mode='HTML')
                    saved_photo = []
                else:
                    saved_photo[:] = saved_photo[:10]
                    media_group = [
                        InputMediaPhoto(media=file_id,
                                        caption=add_b_tags(text, chat_username, chat_id) if i == 0 else None,
                                        parse_mode='HTML')
                        for i, file_id in enumerate(saved_photo)
                    ]
                    messages = bot.send_media_group(
                        chat_id=chat_id,
                        media=media_group,
                    )
                    random_key = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
                    user_photo[random_key] = saved_photo
                    user_text[random_key] = text
                    user_message_id[random_key] = [message.message_id for message in messages]

                    # print(user_photo)

                    approve = [[InlineKeyboardButton("✅Опубликовать", callback_data=f'approve#{chat_id}#{random_key}')],
                               [InlineKeyboardButton("🔙Назад", callback_data='nazad')]]
                    approve_markup = InlineKeyboardMarkup(approve)
                    # bot.send_photo(chat_id, caption=add_b_tags(text), photo=saved_photo, reply_markup=approve_markup,
                    #                      parse_mode='HTML')
                    bot.send_message(
                        chat_id=chat_id,
                        text='👆🏻Пост выше👆🏻',
                        reply_markup=approve_markup,
                    )

                # bot.send_media_group(chat_id,caption=add_b_tags(text),photo=saved_photo,reply_markup=approve_markup,parse_mode='HTML')
            else:
                text = bot.send_message(chat_id, text=add_b_tags(text, chat_username, chat_id),
                                        reply_markup=approve_markup, parse_mode='HTML')

            # saved_photo=[]

            user_states.pop(chat_id)
        elif user_states.get(chat_id) == 'awaiting_admin':
            success_count = 0
            failure_count = 0

            profiles = Telegram_users.objects.all()
            for item in profiles:
                try:
                    if 'photo' in message:
                        response = bot.send_photo(item.user_id, photo=message['photo'][0]['file_id'],
                                                  caption=message.get('caption', ''))

                    elif 'video' in message:
                        response = bot.send_video(item.user_id, video=message['video']['file_id'],
                                                  caption=message.get('caption', ''))
                    else:
                        response = bot.send_message(chat_id=item.user_id, text=message_text)
                    success_count += 1
                except Exception as e:
                    failure_count += 1
                    item.active = True
                    item.save()
                    # print(f"Failed to send to {item.user_id}: {e}")

            approve_ads = [[InlineKeyboardButton("🔙Меню", callback_data='statics_nazad')]]
            approve_ads_markup = InlineKeyboardMarkup(approve_ads)
            bot.send_message(chat_id,
                             text=f"✅ Рассылка успешно отправлена пользователям бота. Удалось отправить: {success_count} Не удалось отправить: {failure_count}",
                             reply_markup=approve_ads_markup)
            user_states.pop(chat_id)

        elif user_states.get(chat_id) == 'awaiting_ban':
            text = f"👤 Вы выбрали пользователя с ID: {message_text}. Выберите действие:"
            try:
                profile = Telegram_users.objects.filter(user_id=message_text).first()
                if profile:
                    if profile.block == True:
                        block = [[InlineKeyboardButton("🔓 Разблокировать", callback_data=f'unblock#{message_text}')],
                                 [InlineKeyboardButton("🔙Назад", callback_data='ban')]
                                 ]
                        block_markup = InlineKeyboardMarkup(block)
                        bot.send_message(chat_id=admin, text=text, reply_markup=block_markup)
                    elif profile.block == False:
                        block = [[InlineKeyboardButton("❌ Заблокировать", callback_data=f'block#{message_text}')],
                                 [InlineKeyboardButton("🔙Назад", callback_data='ban')]
                                 ]
                        block_markup = InlineKeyboardMarkup(block)
                        bot.send_message(chat_id=admin, text=text, reply_markup=block_markup)
                else:
                    bot.send_message(chat_id=admin, text="❌Этот пользователь ещё не запускал бота")

            except Exception as e:
                pass

            user_states.pop(chat_id)


user_selected_category = {}
user_selected_category_go = {}
user_selected_mode = {}


def generate_category_keyboard(chat_id):
    global user_selected_category
    categories = [
        ("ПК", 'pc'),
        ("Товары для компьютера", 'pc_comp'),
        ("Комплектующие для компьютера", 'pc_comp1'),
        ("Серверное оборудование", 'pc_server'),
        ("Сетевое оборудование", 'pc_network'),
        ("Офисная техника и расходники", 'pc_office'),
        ("Телефоны", 'pc_phone'),
        ("Программное обеспечение", 'pf_software'),
    ]

    continue_key = []

    for category_name, callback_value in categories:
        # If the category is selected, add a ✅ next to it
        if chat_id in user_selected_category and callback_value in user_selected_category.get(chat_id):
            category_button = InlineKeyboardButton(f"✅ {category_name}", callback_data=callback_value)
        else:
            category_button = InlineKeyboardButton(category_name, callback_data=callback_value)

        continue_key.append([category_button])

    # Add buttons for "Продолжить", "Искать", and "Назад"
    continue_key.extend([
        [InlineKeyboardButton("Все", callback_data='pc_all')],
        [InlineKeyboardButton("➡️Продолжить", callback_data='pc_go')],
        [InlineKeyboardButton("🔍Искать", callback_data='pc_search')],  # pc_search
        [InlineKeyboardButton("🔙Назад", callback_data='back_top')],
    ])

    return InlineKeyboardMarkup(continue_key)


def generate_category_keyboard_all(chat_id):
    global user_selected_category, user_selected_mode
    categories = [
        ("ПК", 'pc'),
        ("Товары для компьютера", 'pc_comp'),
        ("Комплектующие для компьютера", 'pc_comp1'),
        ("Серверное оборудование", 'pc_server'),
        ("Сетевое оборудование", 'pc_network'),
        ("Офисная техника и расходники", 'pc_office'),
        ("Телефоны", 'pc_phone'),
        ("Программное обеспечение", 'pf_software'),
    ]

    continue_key = []

    for category_name, callback_value in categories:
        category_button = InlineKeyboardButton(f"✅ {category_name}", callback_data=callback_value)
        continue_key.append([category_button])

        if chat_id not in user_selected_category:
            user_selected_category[chat_id] = [callback_value]

        else:
            user_selected_category[chat_id].append(callback_value)

    # user_selected_category[chat_id] = [selected_category]

    # Add buttons for "Продолжить", "Искать", and "Назад"
    continue_key.extend([
        [InlineKeyboardButton("Все", callback_data='pc_all')],
        [InlineKeyboardButton("➡️Продолжить", callback_data='pc_go')],
        [InlineKeyboardButton("🔍Искать", callback_data='pc_search')],  # pc_search
        [InlineKeyboardButton("🔙Назад", callback_data=f'back_top')],
    ])

    return InlineKeyboardMarkup(continue_key)


def process_callback_query(json_data):
    global skip_catergory, skip_pod_category, skip_pod_pod_category, call, user_selected_category, user_selected_mode, user_photo, user_text, saved_photo, user_message_id

    query = json_data['callback_query']
    chat_id = query['message']['chat']['id']

    # chat_name=query['message']['chat']['first_name']
    message_id = query['message']['message_id']

    callback_data_message = query['data']

    if callback_data_message == "ads":
        statics_bot = Telegram_users.objects.all().count()
        active = 0
        fetch_profile = Telegram_users.objects.all()
        for item in fetch_profile:
            try:
                check = bot.send_message(chat_id=item.user_id, text=".")
                bot.delete_message(chat_id=item.user_id, message_id=check.message_id)
                active += 1
            except Exception as e:
                print(e)
        active = 0

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"📢 Вы можете разместить свою рекламу на нашем канале и в боте !\n\nТекущая статистика:  📊 Общее количество пользователей: \n{statics_bot} \n👥 Активные пользователи: {active}   \n\nПожалуйста, введите текст вашей рекламы. После отправки ваша заявка будет обработана, и администратор свяжется с вами!"

        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=nazad_markup

        )

        user_states[chat_id] = 'awaiting_ad_text'


    elif callback_data_message == "support":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="💬 Здесь вы можете задать вопрос нашей поддержке. Напишите Ваше сообщение в чат, и мы ответим Вам в ближайшее время!"

        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=nazad_markup
        )
        user_states[chat_id] = 'awaiting_support_text'

    elif callback_data_message == "nazad":
        try:
            user_states.pop(chat_id)
        except Exception as e:
            pass
            # print(e)
        bot.delete_message(chat_id, message_id=message_id)
        bot.send_message(chat_id, text="Меню")
    elif callback_data_message == 'back_top':
        try:
            user_selected_mode.pop(chat_id)
        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍 Выберите категорию для поиска объявлений"

        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=top_category_markup
        )

        # bot.edit_message_text(
        #     chat_id=chat_id,
        #     message_id=message_id,
        #     text="Меню:"  # Update the message text
        # )
        #
        # bot.edit_message_reply_markup(
        #     chat_id=chat_id,
        #     message_id=query['message']['message_id'],
        #     reply_markup=inline_markup
        # )

    # elif callback_data_message == "pc_continue":
    #
    #     pc_continue = [
    #         [InlineKeyboardButton("Стационарные ПК", callback_data='pc_desktop')],
    #         [InlineKeyboardButton("Ноутбуки", callback_data='pc_laptop')],
    #         [InlineKeyboardButton("Моноблоки", callback_data='pc_desktop')],
    #         [InlineKeyboardButton("Планшеты", callback_data='pc_monoblock')],
    #         [InlineKeyboardButton("➡️Продолжить", callback_data='pc_post')],
    #         [InlineKeyboardButton("🔍Искать", callback_data='pc_search')],
    #         [InlineKeyboardButton("🔙Назад", callback_data='category')],
    #
    #     ]
    #     pc_continue_markup = InlineKeyboardMarkup(pc_continue)
    #
    #     bot.edit_message_text(
    #         chat_id=chat_id,
    #         message_id=message_id,
    #         text="🔽 Выберите подкатегорию, отмечая её галочкой ✅. Или же, можете пропустить этот шаг и просто нажать «➡️Продолжить» ."
    #     )
    #
    #     bot.edit_message_reply_markup(
    #         chat_id=chat_id,
    #         message_id=query['message']['message_id'],
    #         reply_markup=pc_continue_markup
    #     )
    elif callback_data_message.startswith('block'):
        user = callback_data_message.split('#')[1]

        profile = Telegram_users.objects.filter(user_id=user).first()
        profile.block = True
        profile.save()

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"🚫 Пользователь с ID: {user} заблокирован. Он больше не сможет использовать бота."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=block_or_unblock_markup
        )
    elif callback_data_message.startswith('unblock'):
        user = callback_data_message.split('#')[1]

        profile = Telegram_users.objects.filter(user_id=user).first()
        profile.block = False
        profile.save()

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"✅ Пользователь с ID: {user} успешно разблокирован. Теперь он снова имеет доступ к боту."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=block_or_unblock_markup
        )


    elif callback_data_message.startswith('category'):
        text = "🔍 Выберите категорию для поиска объявлений. Вы можете отметить несколько вариантов, отметив их кнопкой ✅   Чтобы перейти дальше, нажмите «➡️Продолжить»."
        try:
            user_selected_mode[chat_id] = callback_data_message.split("#")[1]

        except:
            pass

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






    elif callback_data_message in ['pc', 'pc_comp', 'pc_comp1', 'pc_network', 'pc_office', 'pc_phone', 'pf_software',
                                   'pc_server']:
        selected_category = callback_data_message

        if chat_id in user_selected_category and selected_category in user_selected_category.get(chat_id):
            user_selected_category[chat_id].remove(selected_category)


        else:
            if chat_id not in user_selected_category:
                user_selected_category[chat_id] = [selected_category]

            else:
                user_selected_category[chat_id].append(selected_category)

        text = "🔍 Выберите категорию для поиска объявлений. Вы можете отметить несколько вариантов, отметив их кнопкой ✅   Чтобы перейти дальше, нажмите «➡️Продолжить»."
        continue_markup = generate_category_keyboard(chat_id)
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

    elif callback_data_message == 'pc_go':
        list_pod=[]
        search_pod_pc = [
            [InlineKeyboardButton("Стационарные_ПК", callback_data='#')],
            [InlineKeyboardButton("Ноутбуки", callback_data='#')],
            [InlineKeyboardButton("Моноблоки", callback_data='#')],
            [InlineKeyboardButton("Планшеты", callback_data='#')],
        ]
        search_pod_items = [
            [InlineKeyboardButton("Мониторы", callback_data='#')],
            [InlineKeyboardButton("Клавиатуры_и_мыши", callback_data='#')],
            [InlineKeyboardButton("Акссесуары", callback_data='#')],
            [InlineKeyboardButton("Планшеты", callback_data='#')],
        ]
        search_pod_server = [
            [InlineKeyboardButton("Серверы", callback_data='#')],
            [InlineKeyboardButton("Жёсткие_диски", callback_data='#')],
            [InlineKeyboardButton("Процессоры ", callback_data='#')],
        ]


        selected_categories = user_selected_category.get(chat_id)
        if 'pc' in selected_categories:
            list_pod.extend(search_pod_pc)
        if 'pc_server' in selected_categories:
            list_pod.extend(search_pod_server)
        if 'pc_comp' in selected_categories:
            list_pod.extend(search_pod_server)

        list_pod.extend([
            [InlineKeyboardButton("Все", callback_data='pc_test')],
            [InlineKeyboardButton("➡️Продолжить", callback_data='pc_search')],
            [InlineKeyboardButton("🔍Искать", callback_data='pc_search')],
            [InlineKeyboardButton("🔙Назад", callback_data='category')]
        ])

        continue_markup = InlineKeyboardMarkup(list_pod)

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text='🔽 Выберите подкатегорию, отмечая её галочкой ✅. Или же, можете пропустить этот шаг и просто нажать «➡️Продолжить» .'
        )
        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=continue_markup
        )
    elif callback_data_message == 'pc_test':
        if chat_id in user_selected_category_go:
            user_selected_category_go.pop(chat_id)
            continue_button = [[InlineKeyboardButton("test", callback_data='pc_test')],
                               [InlineKeyboardButton("Все", callback_data='pc_test')],
                               [InlineKeyboardButton("➡️Продолжить", callback_data='pc_search')],
                               [InlineKeyboardButton("🔍Искать", callback_data='pc_search')],
                               [InlineKeyboardButton("🔙Назад", callback_data='category')]]
            continue_markup = InlineKeyboardMarkup(continue_button)

        else:
            user_selected_category_go[chat_id] = callback_data_message
            continue_button = [[InlineKeyboardButton("✅ test", callback_data='pc_test')],
                               [InlineKeyboardButton("Все", callback_data='pc_test')],
                               [InlineKeyboardButton("➡️Продолжить", callback_data='pc_search')],
                               [InlineKeyboardButton("🔍Искать", callback_data='pc_search')],
                               [InlineKeyboardButton("🔙Назад", callback_data='category')]]
            continue_markup = InlineKeyboardMarkup(continue_button)

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text='🔽 Выберите подкатегорию, отмечая её галочкой ✅. Или же, можете пропустить этот шаг и просто нажать «➡️Продолжить» .'
        )
        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=continue_markup
        )



    elif callback_data_message == 'pc_all':
        text = "🔍 Выберите категорию для поиска объявлений. Вы можете отметить несколько вариантов, отметив их кнопкой ✅   Чтобы перейти дальше, нажмите «➡️Продолжить»."
        continue_markup = generate_category_keyboard_all(chat_id)
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
    elif callback_data_message.startswith('pc_search'):
        try:
            count = int(callback_data_message.split('#')[1])
        except:
            count = 0

        try:
            mode = None
            if user_selected_mode[chat_id] == 'sell':
                mode = "Продажа"
            elif user_selected_mode[chat_id] == 'buy':
                mode = "Покупка"
            search = user_selected_category.get(chat_id)
            if search:
                if mode:
                    posts = Posts.objects.filter(category__in=search, type=mode)
                else:
                    posts = Posts.objects.filter(category__in=search)
            else:
                if mode:
                    posts = Posts.objects.filter(type=mode)
                else:
                    posts = Posts.objects.all()

            message_count = 0
            if count == len(posts):
                pc_search = [[InlineKeyboardButton("🔙Назад", callback_data='category')]]
                pc_search_markup = InlineKeyboardMarkup(pc_search)
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text="❌К сожалению, по выбранным категориям больше нет доступных постов. Пожалуйста, попробуйте выбрать другие категории или подкатегории."
                )
                bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=pc_search_markup
                )
                user_selected_category.pop(chat_id)
                return

            if posts:

                for item in range(count, len(posts)):
                    item = posts[item]
                    if item.random_key:
                        username = bot.get_chat(item.user_id).username
                        media_group = [
                            InputMediaPhoto(media=file_id, caption=add_b_tags(item.caption, username,
                                                                              item.user_id) if i == 0 else None,
                                            parse_mode='HTML')
                            for i, file_id in enumerate(item.photo)
                        ]

                        sent_message = bot.send_media_group(chat_id=chat_id, media=media_group)
                    else:
                        bot.copy_message(chat_id, from_chat_id=main_id, message_id=item.message_id)

                    bot.send_message(
                        chat_id,
                        text=f"Ссылка на пост: https://t.me/mainbarxolka/{item.message_id}",
                        disable_web_page_preview=True
                    )

                    message_count += 1
                    if message_count == 5:
                        count += message_count

                        continue_button = [[InlineKeyboardButton("⬇️Показать ещё", callback_data=f'pc_search#{count}')],
                                           [InlineKeyboardButton("🔙Меню", callback_data='nazad')]]
                        continue_button_markup = InlineKeyboardMarkup(continue_button)
                        bot.send_message(chat_id,
                                         text='Показаны посты, подходящих под выбранные категории. Чтобы увидеть больше, нажмите кнопку «⬇️Показать ещё».',
                                         reply_markup=continue_button_markup)
                        message_count = 0

                        break

                if message_count != 0:
                    bot.send_message(chat_id,
                                     text='❌К сожалению, по выбранным категориям больше нет доступных постов. Пожалуйста, попробуйте выбрать другие категории или подкатегории.')


            else:
                pc_search = [[InlineKeyboardButton("🔙Назад", callback_data='category')]]
                pc_search_markup = InlineKeyboardMarkup(pc_search)
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text="❌К сожалению, по выбранным категориям больше нет доступных постов. Пожалуйста, попробуйте выбрать другие категории или подкатегории."
                )
                bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=pc_search_markup
                )
            user_selected_category.pop(chat_id)
        except Exception as e:
            pass
            # pc_search = [[InlineKeyboardButton("🔙Назад", callback_data='category')]]
            # pc_search_markup = InlineKeyboardMarkup(pc_search)
            # bot.edit_message_text(
            #     chat_id=chat_id,
            #     message_id=message_id,
            #     text="❌К сожалению, по выбранным категориям больше нет доступных постов. Пожалуйста, попробуйте выбрать другие категории или подкатегории."
            # )
            # bot.edit_message_reply_markup(
            #     chat_id=chat_id,
            #     message_id=message_id,
            #     reply_markup=pc_search_markup
            # )

            # print(e)



    elif callback_data_message == 'more':
        bot.send_message(chat_id,
                         text='❌К сожалению, по выбранным категориям больше нет доступных постов. Пожалуйста, попробуйте выбрать другие категории или подкатегории.')

    elif callback_data_message == "awaiting_description":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="📝 Пожалуйста, пришлите описание."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=nazad_description_markup
        )

        user_states[chat_id] = 'awaiting_description'
    elif callback_data_message == 'awaiting_price':

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="📞 Отправьте свои контактные данные."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=awaiting_description_markup
        )
        user_states[chat_id] = 'awaiting_price'

    elif callback_data_message == "awaiting_city":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="💰 Укажите стоимость товара"
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=awaiting_price_markup
        )
        user_states[chat_id] = 'awaiting_city'



    elif callback_data_message == 'sell' or callback_data_message == 'buy':
        call = callback_data_message
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text_sell
        )

        if callback_data_message == 'sell':
            bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=nazad_markup
            )
        else:
            bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=sell_markup
            )

        saved_photo = []
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
    elif callback_data_message.startswith("cat"):

        try:
            user_states.pop(chat_id)
            skip_catergory = callback_data_message.split('#')[1]
        except:
            pass

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
    elif callback_data_message.startswith("pk"):

        try:
            user_states.pop(chat_id)
            skip_catergory = callback_data_message.split('#')[1]
        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подкатегорию вашего товара"
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=pk_cat_inline_markup
        )
    elif callback_data_message.startswith("items"):

        try:
            user_states.pop(chat_id)
            skip_catergory = callback_data_message.split('#')[1]
        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подкатегорию вашего товара"
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=items_cat_inline_markup
        )
    elif callback_data_message.startswith("server"):

        try:
            user_states.pop(chat_id)
            skip_catergory = callback_data_message.split('#')[1]
        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подкатегорию вашего товара"
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=server_cat_inline_markup
        )

    elif callback_data_message.startswith("pod"):
        try:
            skip_pod_category = callback_data_message.split('#')[1]

        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подподкатегорию вашего товара."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=sell_skip_pod_category_markup
        )
    elif callback_data_message.startswith("personalpc"):
        try:
            skip_pod_category = callback_data_message.split('#')[1]

        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подподкатегорию вашего товара."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=pk_pod_pod_markup
        )
    elif callback_data_message.startswith("nout"):
        try:
            skip_pod_category = callback_data_message.split('#')[1]

        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подподкатегорию вашего товара."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=laptop_pod_pod_markup
        )
    elif callback_data_message.startswith("planshet"):
        try:
            skip_pod_category = callback_data_message.split('#')[1]

        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подподкатегорию вашего товара."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=planshet_pod_pod_markup
        )
    elif callback_data_message.startswith("monoblock"):
        try:
            skip_pod_category = callback_data_message.split('#')[1]

        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подподкатегорию вашего товара."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=monoblock_pod_pod_markup
        )
    elif callback_data_message.startswith("aksessuar"):
        try:
            skip_pod_category = callback_data_message.split('#')[1]

        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подподкатегорию вашего товара."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=aksessuar_pod_pod_markup
        )
    elif callback_data_message.startswith("monitor"):
        try:
            skip_pod_category = callback_data_message.split('#')[1]

        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подподкатегорию вашего товара."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=monitor_pod_pod_markup
        )
    elif callback_data_message.startswith("keyboard"):
        try:
            skip_pod_category = callback_data_message.split('#')[1]

        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подподкатегорию вашего товара."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=keyboard_pod_pod_markup
        )
    elif callback_data_message.startswith("switch"):
        try:
            skip_pod_category = callback_data_message.split('#')[1]

        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подподкатегорию вашего товара."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=server_pod_pod_markup
        )
    elif callback_data_message.startswith("hard"):
        try:
            skip_pod_category = callback_data_message.split('#')[1]

        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подподкатегорию вашего товара."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=hard_pod_pod_markup
        )
    elif callback_data_message.startswith("processor"):
        try:
            skip_pod_category = callback_data_message.split('#')[1]

        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🔍Выберите подподкатегорию вашего товара."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=proccessor_pod_pod_markup
        )
    elif callback_data_message.startswith('skip'):
        try:
            skip_pod_pod_category = callback_data_message.split('#')[1]

        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="📝 Пожалуйста, пришлите описание."
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=nazad_description_markup
        )
        user_states[chat_id] = 'awaiting_description'


    elif callback_data_message.startswith("approve"):
        user_id = callback_data_message.split('#')[1]
        username = bot.get_chat(user_id).username

        random_key = None
        try:
            random_key = callback_data_message.split('#')[2]
        except:
            pass

        if random_key:
            approve_admin = [[InlineKeyboardButton("✅Одобрить", callback_data=f'publish#{user_id}#{random_key}')],
                             [InlineKeyboardButton("❌Отклонить", callback_data=f'reject#{user_id}#{random_key}')]]
            approve_admin_markup = InlineKeyboardMarkup(approve_admin)
        else:
            approve_admin = [[InlineKeyboardButton("✅Одобрить", callback_data=f'publish#{user_id}')],
                             [InlineKeyboardButton("❌Отклонить", callback_data=f'reject#{user_id}')]]
            approve_admin_markup = InlineKeyboardMarkup(approve_admin)

        if 'photo' in query['message']:
            bot.send_photo(group_id, photo=query['message']['photo'][0]['file_id'],
                           caption=add_b_tags(query['message'].get('caption', ''), username, user_id),
                           reply_markup=approve_admin_markup, parse_mode='HTML')
            bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption="✅ Объявление отправлено на модерацию."
            )
            bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=nazad_markup
            )

        else:

            if random_key:
                for item in user_message_id[random_key]:
                    bot.delete_message(chat_id, message_id=item)

                media_group = [
                    InputMediaPhoto(media=file_id,
                                    caption=add_b_tags(user_text[random_key], username, user_id) if i == 0 else None,
                                    parse_mode='HTML')
                    for i, file_id in enumerate(user_photo[random_key])
                ]
                messages = bot.send_media_group(
                    chat_id=group_id,
                    media=media_group,
                )
                bot.send_message(group_id, text='👆🏻Пост выше👆🏻', reply_markup=approve_admin_markup)
                user_message_id[random_key] = [message.message_id for message in messages]




            else:
                bot.send_message(group_id, text=add_b_tags(query['message']['text'], username, user_id),
                                 reply_markup=approve_admin_markup,
                                 parse_mode='HTML')

            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="✅ Объявление отправлено на модерацию."
            )
            bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=nazad_markup
            )











    elif callback_data_message.startswith("publish"):
        user_id = callback_data_message.split('#')[1]
        username = bot.get_chat(user_id).username
        list_id = []
        random_key = None
        try:
            random_key = callback_data_message.split('#')[2]
        except:
            pass

        if call == 'buy':
            if 'photo' in query['message']:
                sent_message = bot.send_photo(main_id, photo=query['message']['photo'][0]['file_id'],
                                              caption=add_b_tags(query['message'].get('caption', ''), username,
                                                                 user_id), parse_mode='HTML')
                text = query['message'].get('caption', '')
            else:
                if random_key:
                    for item in user_message_id[random_key]:
                        bot.delete_message(group_id, message_id=item)
                    media_group = [
                        InputMediaPhoto(media=file_id, caption=add_b_tags(user_text[random_key], username,
                                                                          user_id) if i == 0 else None,
                                        parse_mode='HTML')
                        for i, file_id in enumerate(user_photo[random_key])
                    ]

                    sent_message = bot.send_media_group(chat_id=main_id, media=media_group)
                    list_id = [message.message_id for message in sent_message]

                    sent_message = sent_message[0]  # The first message in the media group
                    text = user_text[random_key]

                    # user_photo.pop(random_key)
                    # user_text.pop(random_key)
                else:
                    sent_message = bot.send_message(main_id,
                                                    text=add_b_tags(query['message']['text'], username, user_id),
                                                    parse_mode='HTML')
                    text = query['message']['text']

        else:
            if 'photo' in query['message']:
                sent_message = bot.send_photo(main_id, photo=query['message']['photo'][0]['file_id'],
                                              caption=add_b_tags(query['message'].get('caption', ''), username,
                                                                 user_id), reply_markup=bron_markup, parse_mode='HTML')
                text = query['message'].get('caption', '')
            else:
                if random_key:
                    for item in user_message_id[random_key]:
                        bot.delete_message(group_id, message_id=item)
                    media_group = [
                        InputMediaPhoto(media=file_id, caption=add_b_tags(user_text[random_key], username,
                                                                          user_id) if i == 0 else None,
                                        parse_mode='HTML')
                        for i, file_id in enumerate(user_photo[random_key])
                    ]

                    sent_message = bot.send_media_group(chat_id=main_id, media=media_group)
                    list_id = [message.message_id for message in sent_message]

                    sent_message = sent_message[0]
                    bron_pub = [
                        [InlineKeyboardButton("📝Забронировать", callback_data=f'bron#{sent_message.message_id}')]]
                    bron_pub_markup = InlineKeyboardMarkup(bron_pub)
                    bot.send_message(main_id, text='👆🏻Пост выше👆🏻', reply_markup=bron_pub_markup)
                    text = user_text[random_key]

                    # user_photo.pop(random_key)
                    # user_text.pop(random_key)

                    # first_message_id = first_sent_message.message_id



                else:
                    sent_message = bot.send_message(main_id,
                                                    text=add_b_tags(query['message']['text'], username, user_id),
                                                    reply_markup=bron_markup, parse_mode='HTML')
                    text = query['message']['text']

        lines = text.split("\n")
        category = None
        pod = None
        type = None

        for line in lines:
            if line.startswith("Тип:"):
                type = line.split(": #")[1]
            if line.startswith("Категория:"):
                category = line.split(": #")[1]
                if category.startswith('ПК'):
                    category = 'pc'
                elif category.startswith('Товары'):
                    category = 'pc_comp'
                elif category.startswith('Комплектующие'):
                    category = 'pc_comp1'
                elif category.startswith('Серверное'):
                    category = 'pc_server'
                elif category.startswith('Сетевое'):
                    category = 'pc_network'
                elif category.startswith('Офисная'):
                    category = 'pc_office'
                elif category.startswith('Программное'):
                    category = 'pf_software'
            elif line.startswith("Подкатегория:"):
                pod = line.split(": #")[1]

        Posts.objects.create(
            user_id=user_id,
            message_id=sent_message.message_id,
            category=category,
            category_pod=pod,
            type=type,
            random_key=random_key or None,
            user_message_id=list_id,
            caption=user_text.get(random_key, None),
            photo=user_photo.get(random_key, None)
        )

        bot.send_message(user_id,
                         text=f'🎉Ваш пост был успешно одобрен администратором и опубликован на канале! Ссылка на пост:https://t.me/mainbarxolka/{sent_message.message_id}',
                         disable_web_page_preview=True)
        bot.delete_message(chat_id=group_id, message_id=message_id)
        if random_key:
            user_photo.pop(random_key)
            user_text.pop(random_key)
            user_message_id.pop(random_key)



    elif callback_data_message.startswith('bron'):
        id_message = message_id
        try:
            id_message = callback_data_message.split('#')[1]

        except:
            pass

        bron_rejecet = [[InlineKeyboardButton("❌Забронировано", callback_data='empty')]]
        bron_rejecet_markup = InlineKeyboardMarkup(bron_rejecet)
        bot.edit_message_reply_markup(
            chat_id=main_id,
            message_id=message_id,
            reply_markup=bron_rejecet_markup
        )
        name = query.get('from', {}).get('first_name', 'Unknown')
        user = query['from']['id']
        profile = Posts.objects.filter(message_id=id_message).first()
        if profile:
            mention_text = f"[{name}](tg://user?id={user})"
            notify_rejecet = [[InlineKeyboardButton("❌Не хочет", callback_data=f'notify_rejecet#{message_id}#{user}')]]
            notify_rejecet_markup = InlineKeyboardMarkup(notify_rejecet)

            bot.send_message(chat_id=profile.user_id,
                             text=f"📝 Ваше объявление забронировано пользователем {mention_text}. Свяжитесь с ним для уточнения деталей.\n\n  Ссылка на пост:https://t.me/mainbarxolka/{profile.message_id}",
                             reply_markup=notify_rejecet_markup, parse_mode="Markdown", disable_web_page_preview=True)






    elif callback_data_message.startswith('notify_rejecet'):

        try:
            id_message = callback_data_message.split('#')[1]
            id_user = callback_data_message.split('#')[2]
            bron_pub = [[InlineKeyboardButton("📝Забронировать", callback_data=f'bron#{id_message}')]]
            bron_pub_markup = InlineKeyboardMarkup(bron_pub)

            bot.edit_message_reply_markup(
                chat_id=main_id,
                message_id=id_message,
                reply_markup=bron_pub_markup
            )
            bot.delete_message(chat_id=id_user, message_id=message_id)
            bot.send_message(chat_id=id_user, text=f"🔓 Кнопка 📝Забронировать снова активирована для вашего объявления.")
        except Exception as e:
            pass


    elif callback_data_message.startswith('reject'):
        user_id = callback_data_message.split('#')[1]
        random_key = None
        try:
            random_key = callback_data_message.split('#')[2]
        except:
            pass
        if random_key:
            bot.send_message(chat_id=user_id, text='❌Ваш пост был отклонен администрацией.')

            for item in user_message_id[random_key]:
                bot.delete_message(group_id, message_id=item)
            bot.delete_message(chat_id=group_id, message_id=message_id)
            user_photo.pop(random_key)
            user_text.pop(random_key)



        else:
            bot.send_message(chat_id=user_id, text='❌Ваш пост был отклонен администрацией.')
            bot.copy_message(chat_id=user_id, from_chat_id=group_id, message_id=message_id)
            bot.delete_message(chat_id=group_id, message_id=message_id)





    elif callback_data_message == "posts":
        try:
            post = Posts.objects.filter(user_id=chat_id)
            for item in post:
                delete_post = [[InlineKeyboardButton("❌Удалить", callback_data=f'delete_posts#{item.message_id}')]]
                delete_post_markup = InlineKeyboardMarkup(delete_post)
                bot.copy_message(item.user_id, from_chat_id=main_id, message_id=item.message_id,
                                 reply_markup=delete_post_markup)





        except Exception as e:
            pass
            # print(e)


    elif callback_data_message.startswith('delete_posts'):
        delete_message = callback_data_message.split('#')[1]
        last = 0
        # print(delete_message)
        # print(user_message_id)
        # for item in user_message_id[int(delete_message)]:
        #
        #     print(item)
        #     #bot.delete_message(main_id, message_id=item)

        try:
            if 'photo' in query['message']:
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption='❌Этот пост был удалён с канала.'
                )
            else:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text='❌Этот пост был удалён с канала.'
                )

            try:
                posts = Posts.objects.filter(message_id=delete_message).first()
                for item in posts.user_message_id:
                    bot.delete_message(main_id, message_id=item)
                    last = item
            except Exception as e:
                pass

            if last:
                bot.delete_message(main_id, message_id=last + 1)
            else:
                bot.delete_message(main_id, message_id=delete_message)

            Posts.objects.filter(message_id=delete_message).delete()



        except Exception as e:
            print(e)
    elif callback_data_message == 'statics':
        # member_count=bot.get_chat_member_count(chat_id)

        profile_count = Telegram_users.objects.all().count()
        # profile_active=Telegram_users.objects.filter(active=False).count()

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Текущая статистика:\n\n📊 Общее количество пользователей в боте: {profile_count} \n👥 Активные пользователи в боте: {fetch_active(chat_id)}"
        )
        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=statics_nazad_markup
        )
    elif callback_data_message == 'statics_nazad':
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=admin_menu_text
        )
        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=admin_keyboard_markup
        )

    elif callback_data_message == 'admin_ads':
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text='💬Введите текст сообщения для рассылки.'
        )
        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=statics_nazad_markup
        )
        user_states[chat_id] = 'awaiting_admin'

    elif callback_data_message == 'ban':
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text='👤Введите id пользователя которого хотите заблокировать/разблокировать'
        )
        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=statics_nazad_markup
        )
        user_states[chat_id] = 'awaiting_ban'


def index(request):
    return HttpResponse("Hello, World!")

