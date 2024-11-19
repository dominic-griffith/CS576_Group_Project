import logging
import json
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, CallbackQueryHandler, CommandHandler, filters
from services.message_service import MessageService

# Ruta al archivo de configuración
CONFIG_PATH = "../service_manager.json"

class TelegramBot(MessageService):
    def __init__(self):
        super().__init__()
        self.application = None  # Instancia del bot de Telegram
        self.token = None  # API key

    def load_config(self, config):
        """
        Cargar la configuración desde el archivo JSON.
        """
        if "api_key" not in config:
            return False, "No API Key provided."
        self.token = config["api_key"]
        if not self.token:
            return False, "Invalid API key provided."
        return True, None


    def run_service(self):
        """
        Iniciar el servicio del bot de Telegram en un hilo separado con su propio loop de eventos.
        """
        self.application = ApplicationBuilder().token(self.token).build()

        # Registrar handlers
        self._register_handlers()

        # Crear un nuevo loop de eventos para el hilo actual
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Iniciar el bot con el nuevo loop de eventos
        print("Starting Telegram bot...")
        try:
            self.application.run_polling()
        finally:
            loop.close()  # Asegúrate de cerrar el loop al finalizar


    def stop_service(self):
        """
        Detener el servicio.
        """
        if self.application:
            self.application.stop()
            print("Telegram bot stopped.")

    def _register_handlers(self):
        """
        Registrar los handlers para el bot.
        """
        menu_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.send_menu)
        button_handler = CallbackQueryHandler(self.button_callback)

        self.application.add_handler(menu_handler)
        self.application.add_handler(button_handler)

        # Registrar comandos dinámicos
        self._register_dynamic_commands()

    def _register_dynamic_commands(self):
        """
        Registrar comandos dinámicos basados en las acciones.
        """
        for action in ACTIONS.keys():
            async def dynamic_command(update, context, action=action):
                await self.handle_action(update, context, action)
            self.application.add_handler(CommandHandler(action, dynamic_command))

    async def send_menu(self, update, context: ContextTypes.DEFAULT_TYPE):
        """
        Enviar el menú de botones.
        """
        keyboard = [
            [InlineKeyboardButton(action.replace("_", " ").capitalize(), callback_data=action)]
            for action in ACTIONS.keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Determinar el chat_id dependiendo de si es un comando o un botón
        chat_id = (
            update.message.chat_id if update.message
            else update.callback_query.message.chat_id
        )

        # Enviar el menú al usuario
        await context.bot.send_message(
            chat_id=chat_id,
            text="Choose an action:",
            reply_markup=reply_markup
        )

    async def button_callback(self, update, context: ContextTypes.DEFAULT_TYPE):
        """
        Manejar los botones del menú.
        """
        query = update.callback_query
        await self.handle_action(update, context, query.data)

    async def handle_action(self, update, context: ContextTypes.DEFAULT_TYPE, action: str):
        """
        Manejar las acciones para botones y comandos.
        """
        response = ACTIONS.get(action, "Action not recognized.")
        chat_id = (
            update.callback_query.message.chat_id if update.callback_query
            else update.message.chat_id
        )

        # Enviar el mensaje de feedback
        if update.callback_query:
            await update.callback_query.answer()
            await context.bot.send_message(chat_id=chat_id, text=response)
        else:
            await context.bot.send_message(chat_id=chat_id, text=response)

        # Enviar el menú de botones nuevamente
        await self.send_menu(update, context)


    def send_message(self, message, in_response_to):
        """
        Enviar un mensaje al chat de Telegram.
        """
        # Implementación para enviar mensajes
        print(f"Sending message: {message} (in response to: {in_response_to})")

    def await_message(self):
        """
        Esperar un mensaje desde Telegram.
        """
        # Esta función no es usada directamente porque Telegram maneja eventos asincrónicamente.
        pass

# Diccionario de acciones y respuestas
ACTIONS = {
    "turn_light_on": "💡 ON!",
    "turn_light_off": "💡 OFF!",
    "open_door": "Door opened!🔓",
    "lock_door": "Door locked!🔒",
    "cam_1": "Sending image from cam 1!📷",
    "cam_2": "Sending image from cam 2!📷"
}
