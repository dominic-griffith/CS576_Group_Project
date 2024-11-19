"""
- Install dependencies
- Add key to .env file
- Run 'python TelegramBot.py'
- Look for @AutummnTree_Bot on Telegram

TODO:
- Convert to a class like DiscordBot
- Integrate with Home Assistant
"""


import logging
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, CallbackQueryHandler, CommandHandler, filters

# Ruta al archivo de configuración
CONFIG_PATH = os.path.expanduser("./service_manager.json")

def load_api_key(service_name):
    try:
        with open(CONFIG_PATH, 'r') as file:
            config = json.load(file)
            return config["services"][service_name]["api_key"]
    except FileNotFoundError:
        print(f"Config file not found: {CONFIG_PATH}")
    except KeyError:
        print(f"API key for {service_name} not found in config")
    return None

# Cargar la API key de Telegram desde el archivo JSON
API_KEY = load_api_key("telegram")

if not API_KEY:
    raise ValueError("Telegram API key not found. Please check your configuration file.")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Diccionario centralizado de acciones y respuestas
ACTIONS = {
    "turn_light_on": "💡 ON!",
    "turn_light_off": "💡 OFF!",
    "open_door": "Door opened!🔓",
    "lock_door": "Door locked!🔒",
    "cam_1": "Sending image from cam 1!📷",
    "cam_2": "Sending image from cam 2!📷"
}

# Función para enviar el menú de botones
async def send_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(action.replace("_", " ").capitalize(), callback_data=action)]
        for action in ACTIONS.keys()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    chat_id = (
        update.message.chat_id if update.message 
        else update.callback_query.message.chat_id
    )
    
    await context.bot.send_message(
        chat_id=chat_id,
        text="Choose an action:",
        reply_markup=reply_markup
    )

# Función genérica para manejar acciones (tanto botones como comandos)
async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
    chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
    response = ACTIONS.get(action, "Action not recognized.")  # Obtener respuesta del diccionario
    
    # Responder el mensaje
    if update.callback_query:
        # Si es un botón, edita el mensaje
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=response)
    else:
        # Si es un comando, responde normalmente
        await context.bot.send_message(chat_id=chat_id, text=response)
    
    # Reenviar el menú de botones después de dar el feedback
    await send_menu(update, context)

# Función para manejar botones
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    action = query.data
    await handle_action(update, context, action)

# Función para registrar los comandos dinámicamente
def register_dynamic_commands(application):
    for action in ACTIONS.keys():
        command = action  # Comando será igual al nombre de la acción
        async def dynamic_command(update: Update, context: ContextTypes.DEFAULT_TYPE, action=action):
            await handle_action(update, context, action)
        
        # Registrar el comando
        application.add_handler(CommandHandler(command, dynamic_command))

if __name__ == '__main__':
    application = ApplicationBuilder().token(API_KEY).build()
    
    # Enviar el menú cuando el usuario manda el primer mensaje
    menu_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), send_menu)
    button_handler = CallbackQueryHandler(button_callback)

    # Añadir handlers para botones y comandos dinámicos
    application.add_handler(menu_handler)
    application.add_handler(button_handler)
    register_dynamic_commands(application)
    
    application.run_polling()
