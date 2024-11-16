from django.http import HttpResponse
from django.shortcuts import render
import json
import telegram
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import re
from .models import Posts,Telegram_users
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton,WebAppInfo
group_id=-4587708639
main_id=-4563354620
admin=531080457
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


admin_keyboard=[
                    [InlineKeyboardButton("🚀Рассылка", callback_data='admin_ads')],
                    [InlineKeyboardButton("📊Статистика", callback_data='statics')]
                ]
admin_keyboard_markup = InlineKeyboardMarkup(admin_keyboard)
admin_menu_text="👋Добро пожаловать в административную панель."

statics_nazad = [[InlineKeyboardButton("🔙Назад", callback_data='statics_nazad')]]
statics_nazad_markup = InlineKeyboardMarkup(statics_nazad)
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
    [InlineKeyboardButton("💻ПК", callback_data='cat#ПК')],
    [InlineKeyboardButton("🖥️Товары для компьютера", callback_data='cat#Товары_для_компьютера')],
    [InlineKeyboardButton("🛠️Комплектующие для компьютера", callback_data='cat#Комплектующие_для_компьютера')],
    [InlineKeyboardButton("🖧Серверное оборудование", callback_data='cat#Серверное_оборудование')],
    [InlineKeyboardButton("🌐Сетевое оборудование", callback_data='cat#Сетевое_оборудование')],
    [InlineKeyboardButton("🖨️Офисная техника и расходники", callback_data='cat#Офисная_техника_и_расходники')],
    [InlineKeyboardButton("📱Телефоны", callback_data='cat#Телефоны')],
    [InlineKeyboardButton("💿Программное обеспечение", callback_data='cat#Программное_обеспечение')],
    [InlineKeyboardButton("🔙Назад", callback_data='sell')],

]
sell_skip_markup = InlineKeyboardMarkup(sell_skip)
sell_skip_pod = [
    [InlineKeyboardButton("🖥️Стационарные ПК", callback_data='pod#Стационарные_ПК')],
    [InlineKeyboardButton("💻Ноутбуки", callback_data='pod#Ноутбуки')],
    [InlineKeyboardButton("🖨️Моноблоки", callback_data='pod#Моноблоки')],
    [InlineKeyboardButton("📱Планшеты", callback_data='pod#Планшеты')],
    [InlineKeyboardButton("🔙Назад", callback_data='sell_skip')],
]
sell_skip_pod_markup = InlineKeyboardMarkup(sell_skip_pod)

sell_skip_pod_category = [
    [InlineKeyboardButton("🤖Android", callback_data='skip#android')],
    [InlineKeyboardButton("🍎Apple", callback_data='skip#apple')],
    [InlineKeyboardButton("➡️Пропустить", callback_data='skip')],
    [InlineKeyboardButton("🔙Назад", callback_data='cat')],
]
sell_skip_pod_category_markup = InlineKeyboardMarkup(sell_skip_pod_category)
text_category="🔍Выберите категорию вашего товара."

text_sell="📸 Пожалуйста, отправьте фото. Не более 10 штук."
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
saved_photo = None
skip_catergory=None
skip_pod_category=None
skip_pod_pod_category=""
price=None
phone=None
description=None
city=None
nazad_key = [[InlineKeyboardButton("🔙Назад", callback_data='nazad')]]
nazad_markup = InlineKeyboardMarkup(nazad_key)
bron = [[InlineKeyboardButton("📝Забронировать", callback_data='bron')]]
bron_markup = InlineKeyboardMarkup(bron)
call=None
def process_message(json_data):
    global saved_photo,price,description,city,phone
    chat_id = json_data['message']['chat']['id']
    message_text = json_data['message'].get('text', "")
    message=json_data['message']
    chat_username = json_data['message']['chat'].get('username', 'username')
    chat_name = json_data['message']['chat'].get('first_name', 'first_name')

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
        ads = (f"📢 Новая заявка на размещение\nрекламы!\nТекст рекламы:\n{message_text} "
               f"\n💬 Свяжитесь с пользователем\n@{chat_username} для уточнения деталей")
        bot.send_message(group_id, text=ads)
        bot.send_message(chat_id, text="✅ Ваша реклама успешно отправлена! Ожидайте, администратор свяжется с вами для уточнения деталей.")

    elif user_states.get(chat_id) == 'awaiting_support_text':

        support = f"Пользователь @{chat_username} id:{chat_id} написал: {message_text}"

        bot.send_message(group_id, text=support)

    elif user_states.get(chat_id) == "awaiting_photo":
        user_states.pop(chat_id)
        if 'photo' in json_data['message']:
            photo = json_data['message']['photo'][-1]  # Get the highest resolution
            saved_photo = photo['file_id']

            bot.send_message(
                chat_id,
                text=text_category,
                reply_markup=sell_skip_markup
            )
    elif user_states.get(chat_id) == 'awaiting_description':


        description=message_text
        bot.send_message(chat_id,text='📞 Отправьте свои контактные данные.', reply_markup=awaiting_description_markup)
        user_states[chat_id] = 'awaiting_price'
    elif user_states.get(chat_id) == 'awaiting_price':


        phone=message_text
        bot.send_message(chat_id,text='💰 Укажите стоимость товара', reply_markup=awaiting_price_markup)
        user_states[chat_id] = 'awaiting_city'
    elif user_states.get(chat_id) == 'awaiting_city':


        price=message_text
        bot.send_message(chat_id,text='🏙️ Укажите город одним словом или с нижним подчёркиванием.  Например: Санкт_Петербург. (Это нужно для формирования хэштега города, чтобы облегчить поиск).', reply_markup=awaiting_city_markup)
        user_states[chat_id] = 'awaiting_complete'
    elif user_states.get(chat_id) == 'awaiting_complete':
        approve = [[InlineKeyboardButton("✅Опубликовать", callback_data=f'approve#{chat_id}')],
                [InlineKeyboardButton("🔙Назад", callback_data='nazad')]]
        approve_markup = InlineKeyboardMarkup(approve)
        city=message_text

        text = (
            f"Тип:#{'Продажа' if call == 'sell' else 'Покупка'}\n"
            f"Категория: #{skip_catergory}\n"
            f"Подкатегория: #{skip_pod_category}\n"
            f"Подкатегория: #{skip_pod_pod_category}\n"
            f"Пользователь: #{chat_name}\n"
            f"Описание: {description}\n"
            f"Контакты: {phone}\n"
            f"Цена: {price}\n"
            f"Город: #{city}\n"
            f"Автор: @{chat_username}\n"
            f"Отправлено через: @ITbarakholka_bot"
        )
        if saved_photo:
            bot.send_photo(chat_id,caption=text,photo=saved_photo,reply_markup=approve_markup)
        else:
            bot.send_message(chat_id,text=text,reply_markup=approve_markup)

        saved_photo=None

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
                print(f"Failed to send to {item.user_id}: {e}")

        approve_ads = [[InlineKeyboardButton("🔙Меню", callback_data='statics_nazad')]]
        approve_ads_markup = InlineKeyboardMarkup(approve_ads)
        bot.send_message(chat_id,text=f"✅ Рассылка успешно отправлена пользователям бота. Удалось отправить: {success_count} Не удалось отправить: {failure_count}",reply_markup=approve_ads_markup)
        user_states.pop(chat_id)




        # if saved_photo:
        #     bot.send_photo(chat_id,caption=text,photo=saved_photo,reply_markup=approve_markup)
        # else:
        #     bot.send_message(chat_id,text=text,reply_markup=approve_markup)





    else:

        if message_text == '/start':
            try:
                Telegram_users.objects.create(user_id=chat_id)
            except Exception as e:
                print(e)


            text = (f"✨ Привет! Этот бот создан для удобной и быстрой публикации "
                    f"объявлений на канале @ITbarakholka. 🚀 Рад приветствовать тебя, @{chat_username}!")
            bot.send_message(chat_id, text, reply_markup=inline_markup)
        elif message_text == '/admin':
            if chat_id == admin:
                bot.send_message(chat_id,text=admin_menu_text,reply_markup=admin_keyboard_markup)
user_selected_category = {}
def generate_category_keyboard(chat_id):
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
        [InlineKeyboardButton("➡️Продолжить", callback_data='pc_continue')],
        [InlineKeyboardButton("🔍Искать", callback_data='pc_search')], #pc_search
        [InlineKeyboardButton("🔙Назад", callback_data='nazad')],
    ])

    return InlineKeyboardMarkup(continue_key)


def process_callback_query(json_data):
    global skip_catergory,skip_pod_category,skip_pod_pod_category,call
    query = json_data['callback_query']
    chat_id = query['message']['chat']['id']
    message_id=query['message']['message_id']

    callback_data_message = query['data']



    if callback_data_message == "ads":

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="📢 Вы можете разместить свою рекламу на нашем канале и в боте !\n\nТекущая статистика:  📊 Общее количество пользователей: \n1000 \n👥 Активные пользователи: 700   \n\nПожалуйста, введите текст вашей рекламы. После отправки ваша заявка будет обработана, и администратор свяжется с вами!"

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
            print(e)





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

    elif callback_data_message == "category":
        text = "🔍 Выберите категорию для поиска объявлений. Вы можете отметить несколько вариантов, отметив их кнопкой ✅   Чтобы перейти дальше, нажмите «➡️Продолжить»."
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
    elif callback_data_message in ['pc', 'pc_comp', 'pc_comp1', 'pc_network', 'pc_office', 'pc_phone', 'pf_software','pc_server']:
        selected_category=callback_data_message
        if chat_id in user_selected_category and selected_category in user_selected_category.get(chat_id):
            user_selected_category[chat_id].remove(selected_category)

        else:
            if chat_id not in user_selected_category:
                user_selected_category[chat_id]=[selected_category]
            else:
                user_selected_category[chat_id].append(selected_category)



        text = "🔍 Выберите категорию для поиска объявлений. Вы можете отметить несколько вариантов, отметив их кнопкой ✅   Чтобы перейти дальше, нажмите «➡️Продолжить»."
        continue_markup = generate_category_keyboard(chat_id)
        bot.edit_message_text(
        chat_id = chat_id,
        message_id = message_id,
        text = text
        )
        bot.edit_message_reply_markup(
        chat_id = chat_id,
        message_id = message_id,
        reply_markup = continue_markup
        )



    elif callback_data_message == "pc_search":
        try:
            search = user_selected_category.get(chat_id)
            posts = Posts.objects.filter(category__in=search)
            message_count = 0

            if posts:
                for item in posts:
                    bot.copy_message(chat_id, from_chat_id=main_id, message_id=item.message_id)
                    message_count += 1
                    if message_count == 1:
                        continue_button = [[InlineKeyboardButton("⬇️Показать ещё", callback_data='more')],
                                           [InlineKeyboardButton("🔙Меню", callback_data='nazad')]]
                        continue_button_markup = InlineKeyboardMarkup(continue_button)
                        bot.send_message(chat_id,
                                         text='Показаны посты, подходящих под выбранные категории. Чтобы увидеть больше, нажмите кнопку «⬇️Показать ещё».',
                                         reply_markup=continue_button_markup)
                        message_count = 0

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
            print(e)



    elif callback_data_message == 'more':
        bot.send_message(chat_id,text='❌К сожалению, по выбранным категориям больше нет доступных постов. Пожалуйста, попробуйте выбрать другие категории или подкатегории.')

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



    elif callback_data_message == 'sell' or callback_data_message =='buy':
        call=callback_data_message


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
    elif callback_data_message.startswith("cat"):
        try:
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
        user_id=callback_data_message.split('#')[1]
        approve_admin = [[InlineKeyboardButton("✅Одобрить", callback_data=f'publish#{user_id}')],
                   [InlineKeyboardButton("❌Отклонить", callback_data='reject')]]
        approve_admin_markup = InlineKeyboardMarkup(approve_admin)
        if 'photo' in query['message']:
            bot.send_photo(group_id,photo=query['message']['photo'][0]['file_id'],caption=query['message'].get('caption', ''),reply_markup=approve_admin_markup)
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
            bot.send_message(group_id,text=query['message']['text'],reply_markup=approve_admin_markup)
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

        if 'photo' in query['message']:
            sent_message=bot.send_photo(main_id,photo=query['message']['photo'][0]['file_id'],caption=query['message'].get('caption', ''),reply_markup=bron_markup)
            text=query['message'].get('caption', '')
        else:
            sent_message=bot.send_message(main_id,text=query['message']['text'],reply_markup=bron_markup)
            text=query['message']['text']

        lines=text.split("\n")
        category = None
        pod = None

        for line in lines:
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



        Posts.objects.create(user_id=user_id,message_id=sent_message.message_id,category=category,category_pod=pod)


        bot.send_message(user_id,text='🎉Ваш пост был успешно одобрен администратором и опубликован на канале!')
        bot.delete_message(chat_id=group_id, message_id=message_id)

    elif callback_data_message == 'bron':
        bron_rejecet = [[InlineKeyboardButton("❌Забронировано", callback_data='bron_reject')]]
        bron_rejecet_markup = InlineKeyboardMarkup(bron_rejecet)
        bot.edit_message_reply_markup(
            chat_id=main_id,
            message_id=message_id,
            reply_markup=bron_rejecet_markup
        )
        profile=Posts.objects.filter(message_id=message_id).first()
        if profile:
            user=bot.get_chat(profile.user_id)
            username = user.username if user.username else "Пользователь"
            notify_rejecet = [[InlineKeyboardButton("❌Не хочет", callback_data=f'bron_reject#{message_id}')]]
            notify_rejecet_markup = InlineKeyboardMarkup(notify_rejecet)
            bot.send_message(chat_id=profile.user_id,text=f"📝 Ваше объявление забронировано пользователем @{username}. Свяжитесь с ним для уточнения деталей.",reply_markup=notify_rejecet_markup)






    elif callback_data_message.startswith('bron_reject'):
        id_message=callback_data_message.split('#')[1]
        bot.edit_message_reply_markup(
            chat_id=main_id,
            message_id=id_message,
            reply_markup=bron_markup
        )
    elif callback_data_message == "reject":
        bot.delete_message(chat_id=group_id, message_id=message_id)


    elif callback_data_message == "posts":
        try:
            post=Posts.objects.filter(user_id=chat_id)
            for item in post:
                delete_post = [[InlineKeyboardButton("❌Удалить", callback_data=f'delete_posts#{item.message_id}')]]
                delete_post_markup = InlineKeyboardMarkup(delete_post)
                bot.copy_message(item.user_id, from_chat_id=main_id, message_id=item.message_id, reply_markup=delete_post_markup)


        except Exception as e:
            print(e)


    elif callback_data_message.startswith('delete_posts'):
        delete_message=callback_data_message.split('#')[1]

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

            bot.delete_message(main_id, message_id=delete_message)
            Posts.objects.filter(message_id=delete_message).delete()

        except Exception as e:
            print(e)
    elif callback_data_message == 'statics':
        member_count=bot.get_chat_member_count(chat_id)
        profile_count=Telegram_users.objects.all().count()
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Текущая статистика:  📊 Общее количество пользователей канала: {member_count} 👥 Активные пользователи канала: {member_count} 🤖Всего пользователей в боте: {profile_count}"
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






















def index(request):
    return HttpResponse("Hello, World!")

