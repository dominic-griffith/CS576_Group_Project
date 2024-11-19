import logging
import json
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, CallbackQueryHandler, CommandHandler, filters
from services.message_service import MessageService



class TelegramBot(MessageService):
    def __init__(self):
        super().__init__()
        self.application = None  # Telegram bot instance
        self.token = None  # API key

    def load_config(self, config):
        """
        Load the configuration from the JSON file.
        The configuration is provided by the ServiceManager.
        """
        if "api_key" not in config:
            return False, "No API Key provided."
        self.token = config["api_key"]
        if not self.token:
            return False, "Invalid API key provided."
        return True, None


    def run_service(self):
        """
        Start the Telegram bot service in a separate thread with its own event loop.
        """
        self.application = ApplicationBuilder().token(self.token).build()

        # Register handlers
        self._register_handlers()

        # Create a new event loop for the current thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Start the bot with the new event loop
        print("Starting Telegram bot...")
        try:
            self.application.run_polling()
        finally:
            loop.close()  # Ensure the event loop is closed at the end


    def stop_service(self):
        """
        Stop the service.
        """
        if self.application:
            self.application.stop()
            print("Telegram bot stopped.")

    def _register_handlers(self):
        """
        Register handlers for the bot.
        """
        menu_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.send_menu)
        button_handler = CallbackQueryHandler(self.button_callback)

        self.application.add_handler(menu_handler)
        self.application.add_handler(button_handler)

        # Register dynamic commands
        self._register_dynamic_commands()

    def _register_dynamic_commands(self):
        """
        Register dynamic commands based on the actions.
        """
        for action in ACTIONS.keys():
            async def dynamic_command(update, context, action=action):
                await self.handle_action(update, context, action)
            self.application.add_handler(CommandHandler(action, dynamic_command))

    async def send_menu(self, update, context: ContextTypes.DEFAULT_TYPE):
        """
        Send the menu of buttons.
        """
        keyboard = [
            [InlineKeyboardButton(action.replace("_", " ").capitalize(), callback_data=action)]
            for action in ACTIONS.keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Determine the chat_id depending on whether it is a command or a button
        chat_id = (
            update.message.chat_id if update.message
            else update.callback_query.message.chat_id
        )

        # Send the menu to the user
        await context.bot.send_message(
            chat_id=chat_id,
            text="Choose an action:",
            reply_markup=reply_markup
        )

    async def button_callback(self, update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle the menu buttons.
        """
        query = update.callback_query
        await self.handle_action(update, context, query.data)

    async def handle_action(self, update, context: ContextTypes.DEFAULT_TYPE, action: str):
        """
        Handle actions for buttons and commands.
        """
        response = ACTIONS.get(action, "Action not recognized.")
        chat_id = (
            update.callback_query.message.chat_id if update.callback_query
            else update.message.chat_id
        )

        # Send feedback message
        if update.callback_query:
            await update.callback_query.answer()
            await context.bot.send_message(chat_id=chat_id, text=response)
        else:
            await context.bot.send_message(chat_id=chat_id, text=response)

        # Send the menu of buttons again
        await self.send_menu(update, context)


    def send_message(self, message, in_response_to):
        """
        Send a message to the Telegram chat.
        """
        # Implementation for sending messages
        print(f"Sending message: {message} (in response to: {in_response_to})")

    def await_message(self):
        """
        Wait for a message from Telegram.
        """
        # This function is not used directly because Telegram handles events asynchronously.
        pass

# Dictionary of actions and their corresponding responses
ACTIONS = {
    "turn_light_on": "💡 ON!",
    "turn_light_off": "💡 OFF!",
    "open_door": "Door opened!🔓",
    "lock_door": "Door locked!🔒",
    "cam_1": "Sending image from cam 1!📷",
    "cam_2": "Sending image from cam 2!📷"
}
