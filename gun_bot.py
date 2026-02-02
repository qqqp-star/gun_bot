import logging
import random
import json
import os
import time
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
print("🚀 Запускаю гун-бота...")

# ===== ВАЖНО: ДЛЯ RAILWAY =====
import os

# Получаем токен из переменных окружения Railway
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    print("❌ BOT_TOKEN не найден в переменных окружения")
    exit()
print(f"✅ Токен получен из окружения: {TOKEN[:10]}...")

DATA_FILE = 'gun_data.json'
COOLDOWN_FILE = 'cooldowns.json'

# Глобальные переменные для статистики
global_stats = {}
global_cooldowns = {}

# Загрузка данных
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

def save_stats():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(global_stats, f, ensure_ascii=False, indent=2)

def save_cooldowns():
    with open(COOLDOWN_FILE, 'w', encoding='utf-8') as f:
        json.dump(global_cooldowns, f, ensure_ascii=False, indent=2)

# Английские команды для CommandHandler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ГУН-БОТ @BHYTPEHHAYA_NENAVIST!\n\n"
        "💦 Команды:\n"
        "/гунить - Пролить сперму (15-30л) раз в 12ч\n"
        "/топгунеров - Топ\n"
        "/стата - Статистика\n"
        "/помощь - Справка"
    )

async def gun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    # Проверка кулдауна
    current_time = time.time()
    if user_id in global_cooldowns:
        last_gun = global_cooldowns[user_id]
        if current_time - last_gun < 12 * 3600:
            hours_left = int((12 * 3600 - (current_time - last_gun)) / 3600)
            minutes_left = int(((12 * 3600 - (current_time - last_gun)) % 3600) / 60)
            await update.message.reply_text(
                f"⏳ Подожди {hours_left}ч {minutes_left}м до следующего гуна!"
            )
            return
    
    # Гуним
    litres = random.randint(15, 30)
    
    if user_id not in global_stats:
        global_stats[user_id] = {'total': 0, 'count': 0, 'name': user.first_name}
    
    global_stats[user_id]['total'] += litres
    global_stats[user_id]['count'] += 1
    global_cooldowns[user_id] = current_time
    
    save_stats()
    save_cooldowns()
    
    messages = [
        f"💦 БАХ! {user.mention_html()} пролил {litres} литров спермы @BHYTPEHHAYA_NENAVIST!",
        f"🌊 ОГО! {user.mention_html()} выпустил {litres} литров спермы @BHYTPEHHAYA_NENAVIST!",
        f"🚰 ВАУ! {user.mention_html()} пролил {litres} литров спермы @BHYTPEHHAYA_NENAVIST!",
        f"💧 БУМ! {user.mention_html()} выпустил {litres} литров спермы @BHYTPEHHAYA_NENAVIST!",
        f"🌪️ УРАГАН! {user.mention_html()} пролил {litres} литров спермы @BHYTPEHHAYA_NENAVIST!"
    ]
    
    msg = random.choice(messages)
    msg += f"\n\n📊 Всего спермы во мне: {global_stats[user_id]['total']} литров"
    msg += f"\n🎯 Количество писек: {global_stats[user_id]['count']}"
    msg += f"\n⏳ Следующий гун через 12 часов!"
    
    await update.message.reply_text(msg, parse_mode='HTML')
    print(f"📨 {user.first_name} пролил {litres}л")

async def topgunners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not global_stats:
        await update.message.reply_text(
            "📭 Пока никто не гунил на @BHYTPEHHAYA_NENAVIST... Будь первым! /гунить"
        )
        return
    
    sorted_users = sorted(global_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
    msg = "🏆 ТОП ГУНЕРОВ @BHYTPEHHAYA_NENAVIST:\n\n"
    for i, (uid, data) in enumerate(sorted_users, 1):
        name = data.get('name', 'Аноним')
        total = data['total']
        count = data['count']
        
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"{i}."
        
        msg += f"{medal} {name} - {total} литров ({count} раз)\n"
    
    msg += "\n💦 Хочешь в топ? Пиши /гунить (раз в 12 часов)"
    await update.message.reply_text(msg)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    if user_id in global_stats:
        data = global_stats[user_id]
        msg = f"📊 Статистика {user.first_name}:\n\n"
        msg += f"💦 Всего пролито: {data['total']} литров\n"
        msg += f"🎯 Размер пиписьки: {data['count']}\n"
        
        # Проверка кулдауна
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
        msg = "🤷 Ты еще не гунил на @BHYTPEHHAYA_NENAVIST! Напиши /гунить"
    
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
        "💦 @BHYTPEHHAYA_NENAVIST ждет твоей спермы!"
    )

# Обработчик русских команд через MessageHandler
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

def main():
    try:
        application = Application.builder().token(TOKEN).build()
        
        # Английские команды (обязательно!)
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("gun", gun))
        application.add_handler(CommandHandler("topgunners", topgunners))
        application.add_handler(CommandHandler("stats", stats))
        application.add_handler(CommandHandler("help", help_command))
        
        # Русские команды через MessageHandler
        application.add_handler(MessageHandler(
            filters.TEXT & filters.Regex(r'^/(старт|гунить|топгунеров|стата|помощь)(@\w+)?$'),
            handle_russian_command
        ))
        
        print("="*50)
        print("🤖 БОТ ЗАПУЩЕН! Версия для Railway")
        print("📋 Русские команды:")
        print("  /старт       - Информация")
        print("  /гунить      - Пролить сперму (раз в 12 часов)")
        print("  /топгунеров  - Топ гунеров")
        print("  /стата       - Статистика")
        print("  /помощь      - Справка")
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