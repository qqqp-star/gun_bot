import logging
import random
import json
import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)
print("🚀 Запускаю гун-бота...")

# ===== КОНСТАНТЫ =====
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    print("❌ BOT_TOKEN не найден в переменных окружения")
    exit()
print(f"✅ Токен получен из окружения: {TOKEN[:10]}...")

ADMIN_ID = 5631456705          # твой ID
FRIEND_ID = 6604891551          # ID друга, которого нужно пинать

DATA_FILE = 'gun_data.json'
COOLDOWN_FILE = 'cooldowns.json'
SETTINGS_FILE = 'admin_settings.json'

# Глобальные переменные
global_stats = {}
global_cooldowns = {}
admin_settings = {
    'ping_friend_enabled': True   # по умолчанию включено
}

# ===== ЗАГРУЗКА ДАННЫХ =====
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            global_stats = json.load(f)
    except:
        pass

if os.path.exists(COOLDOWN_FILE):
    try:
        with open(COOLDOWN_FILE, 'r', encoding='utf-8') as f:
            global_cooldowns = json.load(f)
    except:
        pass

if os.path.exists(SETTINGS_FILE):
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            admin_settings = json.load(f)
    except:
        pass

# ===== СОХРАНЕНИЕ =====
def save_stats():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(global_stats, f, ensure_ascii=False, indent=2)

def save_cooldowns():
    with open(COOLDOWN_FILE, 'w', encoding='utf-8') as f:
        json.dump(global_cooldowns, f, ensure_ascii=False, indent=2)

def save_settings():
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(admin_settings, f, ensure_ascii=False, indent=2)

# ===== ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ УПОМИНАНИЯ ДРУГА =====
async def get_friend_mention(context: ContextTypes.DEFAULT_TYPE) -> str:
    """Возвращает HTML-упоминание друга (если включено в настройках)."""
    if not admin_settings.get('ping_friend_enabled', True):
        return ''
    try:
        chat = await context.bot.get_chat(FRIEND_ID)
        name = chat.first_name or f"user{FRIEND_ID}"
        return f' <a href="tg://user?id={FRIEND_ID}">{name}</a>'
    except Exception as e:
        logging.error(f"Не удалось получить данные друга: {e}")
        return f' <a href="tg://user?id={FRIEND_ID}">друг</a>'

# ===== ФУНКЦИЯ ДЛЯ ОТПРАВКИ JSON ФАЙЛА (ВЫГРУЗКА) =====
async def send_json_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет файл gun_data.json администратору."""
    if not os.path.exists(DATA_FILE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Файл с данными ещё не создан.")
        return
    try:
        with open(DATA_FILE, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename='gun_data.json',
                caption="Резервная копия данных пользователей."
            )
        logging.info(f"Админ {ADMIN_ID} запросил файл {DATA_FILE}")
    except Exception as e:
        logging.error(f"Ошибка при отправке файла: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Не удалось отправить файл.")

# ===== ОБРАБОТЧИКИ КОМАНД =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ГУН-БОТ!\n\n"
        "💦 Команды:\n"
        "/гунить - Пролить сперму (15-30л) раз в 12ч\n"
        "/топгунеров - Топ\n"
        "/стата - Твоя статистика\n"
        "/помощь - Справка"
    )

async def gun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    current_time = time.time()
    # Проверка кулдауна
    if user_id in global_cooldowns:
        last_gun = global_cooldowns[user_id]
        if current_time - last_gun < 12 * 3600:
            hours_left = int((12 * 3600 - (current_time - last_gun)) / 3600)
            minutes_left = int(((12 * 3600 - (current_time - last_gun)) % 3600) / 60)
            await update.message.reply_text(
                f"⏳ Подожди {hours_left}ч {minutes_left}м до следующего гуна!"
            )
            return
    
    litres = random.randint(15, 30)
    
    # Обновление/создание записи пользователя
    if user_id not in global_stats:
        global_stats[user_id] = {'total': 0, 'count': 0, 'name': user.first_name, 'username': user.username}
    else:
        global_stats[user_id]['name'] = user.first_name
        global_stats[user_id]['username'] = user.username
    
    global_stats[user_id]['total'] += litres
    global_stats[user_id]['count'] += 1
    global_cooldowns[user_id] = current_time
    
    save_stats()
    save_cooldowns()
    
    # Базовые сообщения (без упоминания друга)
    base_messages = [
        f"💦 БАХ! {user.mention_html()} пролил {litres} литров спермы",
        f"🌊 ОГО! {user.mention_html()} выпустил {litres} литров спермы",
        f"🚰 ВАУ! {user.mention_html()} пролил {litres} литров спермы",
        f"💧 БУМ! {user.mention_html()} выпустил {litres} литров спермы",
        f"🌪️ УРАГАН! {user.mention_html()} пролил {litres} литров спермы"
    ]
    
    msg = random.choice(base_messages)
    friend_mention = await get_friend_mention(context)
    if friend_mention:
        msg += friend_mention + "!"
    else:
        msg += "!"
    
    msg += f"\n\n📊 Всего спермы во мне: {global_stats[user_id]['total']} литров"
    msg += f"\n🎯 Количество писек: {global_stats[user_id]['count']}"
    msg += f"\n⏳ Следующий гун через 12 часов!"
    
    await update.message.reply_text(msg, parse_mode='HTML')
    print(f"📨 {user.first_name} пролил {litres}л")

async def topgunners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not global_stats:
        await update.message.reply_text(
            "📭 Пока никто не гунил... Будь первым! /гунить"
        )
        return
    
    sorted_users = sorted(global_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
    msg = "🏆 ТОП ГУНЕРОВ:\n\n"
    for i, (uid, data) in enumerate(sorted_users, 1):
        name = data.get('name', 'Аноним')
        total = data['total']
        count = data['count']
        
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        msg += f"{medal} {name} - {total} литров ({count} раз)\n"
    
    msg += "\n💦 Хочешь в топ? Пиши /гунить (раз в 12 часов)"
    await update.message.reply_text(msg)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статистику пользователя (для всех)."""
    user = update.effective_user
    user_id = str(user.id)
    
    if user_id in global_stats:
        data = global_stats[user_id]
        msg = f"📊 Статистика {user.first_name}:\n\n"
        msg += f"💦 Всего пролито: {data['total']} литров\n"
        msg += f"🎯 Количество писек: {data['count']}\n"
        
        if user_id in global_cooldowns:
            time_left = 12 * 3600 - (time.time() - global_cooldowns[user_id])
            if time_left > 0:
                hours = int(time_left // 3600)
                minutes = int((time_left % 3600) // 60)
                msg += f"\n⏳ До следующего гуна: {hours}ч {minutes}м"
            else:
                msg += "\n✅ Можешь гунить сейчас!"
        else:
            msg += "\n✅ Можешь гунить сейчас!"
    else:
        msg = "🤷 Ты еще не гунил! Напиши /гунить"
    
    msg += "\n🎯 Хочешь трахнуть меня? /гунить"
    await update.message.reply_text(msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Доступные команды:\n\n"
        "/старт - Начало работы\n"
        "/гунить - Пролить сперму (15-30 литров) - раз в 12 часов\n"
        "/топгунеров - Топ гунеров\n"
        "/стата - Твоя статистика\n"
        "/помощь - Эта справка\n\n"
        "💦 Жду твоей спермы!"
    )

# ===== АДМИН-КОМАНДЫ (ТОЛЬКО ДЛЯ ADMIN_ID) =====
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню администратора с настройками."""
    if update.effective_user.id != ADMIN_ID:
        return
    
    status_text = "✅ Включено" if admin_settings['ping_friend_enabled'] else "❌ Выключено"
    keyboard = [
        [InlineKeyboardButton(f"Пинг друга: {status_text}", callback_data="noop")],
        [InlineKeyboardButton("✅ Включить пинг", callback_data="ping_on"),
         InlineKeyboardButton("❌ Выключить пинг", callback_data="ping_off")],
        [InlineKeyboardButton("📤 Выгрузить JSON", callback_data="get_json")],
        [InlineKeyboardButton("📥 Загрузить JSON", callback_data="await_json")],
        [InlineKeyboardButton("🔄 Обновить меню", callback_data="refresh_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔧 Админ-меню\n\n"
        "Выбери действие:",
        reply_markup=reply_markup
    )

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на кнопки в админ-меню."""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("Ты не админ.")
        return
    
    # Обработка разных callback_data
    if query.data == "ping_on":
        admin_settings['ping_friend_enabled'] = True
        save_settings()
        await query.edit_message_text("✅ Пинг друга включён.")
        # Показываем меню заново через новое сообщение (или можно редактировать)
        await show_admin_menu_after_action(query, context)
    
    elif query.data == "ping_off":
        admin_settings['ping_friend_enabled'] = False
        save_settings()
        await query.edit_message_text("❌ Пинг друга выключен.")
        await show_admin_menu_after_action(query, context)
    
    elif query.data == "get_json":
        # Отправляем файл, не трогая меню
        await send_json_file(update, context)
        # Можно дополнительно показать уведомление, но не обязательно
    
    elif query.data == "await_json":
        # Устанавливаем флаг ожидания JSON для админа
        context.user_data['awaiting_json'] = True
        await query.edit_message_text(
            "📥 Режим загрузки JSON активирован.\n"
            "Отправь мне файл .json для восстановления данных.\n"
            "Чтобы отменить, просто ничего не отправляй."
        )
        # После этого можно показать меню заново по кнопке "Обновить"
    
    elif query.data == "refresh_menu":
        # Просто показываем меню заново
        await refresh_admin_menu(query, context)
    
    elif query.data == "noop":
        # Ничего не делаем, просто игнорируем
        pass

async def show_admin_menu_after_action(query, context):
    """Показывает админ-меню после выполнения действия (чтобы не спамить сообщениями)."""
    status_text = "✅ Включено" if admin_settings['ping_friend_enabled'] else "❌ Выключено"
    keyboard = [
        [InlineKeyboardButton(f"Пинг друга: {status_text}", callback_data="noop")],
        [InlineKeyboardButton("✅ Включить пинг", callback_data="ping_on"),
         InlineKeyboardButton("❌ Выключить пинг", callback_data="ping_off")],
        [InlineKeyboardButton("📤 Выгрузить JSON", callback_data="get_json")],
        [InlineKeyboardButton("📥 Загрузить JSON", callback_data="await_json")],
        [InlineKeyboardButton("🔄 Обновить меню", callback_data="refresh_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        "🔧 Админ-меню\n\n"
        "Выбери действие:",
        reply_markup=reply_markup
    )

async def refresh_admin_menu(query, context):
    """Обновляет меню (редактирует текущее сообщение)."""
    status_text = "✅ Включено" if admin_settings['ping_friend_enabled'] else "❌ Выключено"
    keyboard = [
        [InlineKeyboardButton(f"Пинг друга: {status_text}", callback_data="noop")],
        [InlineKeyboardButton("✅ Включить пинг", callback_data="ping_on"),
         InlineKeyboardButton("❌ Выключить пинг", callback_data="ping_off")],
        [InlineKeyboardButton("📤 Выгрузить JSON", callback_data="get_json")],
        [InlineKeyboardButton("📥 Загрузить JSON", callback_data="await_json")],
        [InlineKeyboardButton("🔄 Обновить меню", callback_data="refresh_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "🔧 Админ-меню\n\n"
        "Выбери действие:",
        reply_markup=reply_markup
    )

# ===== ЗАГРУЗКА JSON ОТ АДМИНА (ТОЛЬКО ПОСЛЕ НАЖАТИЯ КНОПКИ) =====
async def handle_admin_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принимает JSON-файл, только если админ нажал кнопку 'Загрузить JSON'."""
    user = update.effective_user
    if user.id != ADMIN_ID:
        return  # Игнорируем документы от других пользователей
    
    # Проверяем флаг ожидания
    if not context.user_data.get('awaiting_json', False):
        await update.message.reply_text("❌ Сначала нажми кнопку 'Загрузить JSON' в админ-меню.")
        return
    
    # Проверяем расширение файла
    if not update.message.document.file_name.endswith('.json'):
        await update.message.reply_text("Пожалуйста, отправьте файл с расширением .json")
        return

    file = await context.bot.get_file(update.message.document.file_id)
    temp_file = f"temp_{DATA_FILE}"
    try:
        await file.download_to_drive(temp_file)

        with open(temp_file, 'r', encoding='utf-8') as f:
            new_data = json.load(f)

        os.replace(temp_file, DATA_FILE)
        global global_stats
        global_stats = new_data

        # Сбрасываем флаг ожидания
        context.user_data['awaiting_json'] = False

        await update.message.reply_text("✅ Данные успешно восстановлены из полученного файла.")
        logging.info(f"Админ {ADMIN_ID} восстановил данные из файла {update.message.document.file_name}")

    except json.JSONDecodeError:
        await update.message.reply_text("❌ Полученный файл не является корректным JSON.")
        if os.path.exists(temp_file):
            os.remove(temp_file)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при обработке файла: {e}")
        logging.error(f"Ошибка при восстановлении данных: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

# ===== ОБРАБОТЧИК РУССКИХ КОМАНД =====
async def handle_russian_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith('/старт'):
        await start(update, context)
    elif text.startswith('/гунить'):
        await gun(update, context)
    elif text.startswith('/топгунеров'):
        await topgunners(update, context)
    elif text.startswith('/стата'):
        await stats(update, context)
    elif text.startswith('/помощь'):
        await help_command(update, context)

# ===== ОСНОВНАЯ ФУНКЦИЯ =====
def main():
    try:
        application = Application.builder().token(TOKEN).build()
        
        # Английские команды
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("gun", gun))
        application.add_handler(CommandHandler("topgunners", topgunners))
        application.add_handler(CommandHandler("stats", stats))
        application.add_handler(CommandHandler("help", help_command))
        
        # Админская команда для вызова меню
        application.add_handler(CommandHandler("гунадмменю", admin_menu))
        
        # Callback для инлайн-кнопок
        application.add_handler(CallbackQueryHandler(admin_callback, pattern="^(ping_on|ping_off|get_json|await_json|refresh_menu|noop)$"))
        
        # Загрузка JSON от админа (только после активации кнопкой)
        application.add_handler(MessageHandler(
            filters.Document.FileExtension("json") & filters.User(user_id=ADMIN_ID),
            handle_admin_document
        ))
        
        # Русские команды
        application.add_handler(MessageHandler(
            filters.TEXT & filters.Regex(r'^/(старт|гунить|топгунеров|стата|помощь)(@\w+)?$'),
            handle_russian_command
        ))
        
        print("="*50)
        print("🤖 БОТ ЗАПУЩЕН!")
        print("📋 Команды для всех:")
        print("  /гунить, /топгунеров, /стата, /помощь")
        print("🔧 Команда для админа:")
        print("  /гунадмменю    - меню настроек и управления JSON")
        print("="*50)
        print("⚡ Бот готов к работе!")
        print("🛑 Нажми Ctrl+C для остановки")
        print("="*50)
        
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()