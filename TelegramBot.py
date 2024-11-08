import logging
import os
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, CallbackQueryHandler, filters


"""
- Install dependencies
- Add key to .env file
- Run 'python TelegramBot.py'
- Look for @AutummnTree_Bot on Telegram

TODO:
- Convert to a class like DiscordBot
- Integrate with Home Assistant

"""






# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API key de las variables de entorno
API_KEY = os.getenv('TELEGRAM_BOT_API_KEY')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Función para enviar el menú de botones
async def send_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Turn light on", callback_data='turn_light_on')],
        [InlineKeyboardButton("Turn light off", callback_data='turn_light_off')],
        [InlineKeyboardButton("Open door", callback_data='open_door')],
        [InlineKeyboardButton("Lock door", callback_data='lock_door')],
        [InlineKeyboardButton("Cam 1", callback_data='cam_1')],
        [InlineKeyboardButton("Cam 2", callback_data='cam_2')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Determinar el chat_id de forma segura
    chat_id = (
        update.message.chat_id if update.message 
        else update.callback_query.message.chat_id
    )
    
    await context.bot.send_message(
        chat_id=chat_id,
        text="Choose an action:",
        reply_markup=reply_markup
    )

# Función para manejar la respuesta de los botones
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Confirma que se presionó el botón

    # Mensajes de respuesta según el botón presionado
    if query.data == 'turn_light_on':
        await query.edit_message_text(text="💡 ON!")
    elif query.data == 'turn_light_off':
        await query.edit_message_text(text="💡 OFF!")
    elif query.data == 'open_door':
        await query.edit_message_text(text="Door opened!🔓")
    elif query.data == 'lock_door':
        await query.edit_message_text(text="Door locked!🔒")
    elif query.data == 'cam_1':
        await query.edit_message_text(text="Sending image from cam 1!📷")
    elif query.data == 'cam_2':
        await query.edit_message_text(text="Sending image from cam 2!📷")

    # Reenviar el menú de botones después de dar el feedback
    await send_menu(update, context)

if __name__ == '__main__':
    application = ApplicationBuilder().token(API_KEY).build()
    
    # Enviar el menú cuando el usuario manda el primer mensaje
    menu_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), send_menu)
    button_handler = CallbackQueryHandler(button_callback)
    
    application.add_handler(menu_handler)
    application.add_handler(button_handler)
    
    application.run_polling()
