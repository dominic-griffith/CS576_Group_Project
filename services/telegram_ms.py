import logging
import json
import asyncio

# Requires pip install of "python-telegram-bot"
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, CallbackQueryHandler, CommandHandler, filters

from services.message_service import MessageService

class TelegramBot(MessageService):
	def __init__(self):
		super().__init__()
		self.application = None  # Telegram bot instance
		self.token = None  # API key

		# A dictionary of string messages and the userMessage object associated with it, we can use
		#   this in send_message along with the "in_response_to" variable to access the incoming
		#   userMessage object
		self.message_metadata = {}

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
		self._register_dynamic_commands()

		self.loop = asyncio.new_event_loop()
		asyncio.set_event_loop(self.loop)

		print("Starting telegram...")
		self.application.run_polling()

	def stop_service(self):
		"""
		Stop the service.
		"""
		print("Attempting to stop telegram (won't work)")
		self.application.shutdown()

	def _register_handlers(self):
		"""
		Register handlers for the bot.
		"""
		menu_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.process_message)
		button_handler = CallbackQueryHandler(self.button_callback)

		self.application.add_handler(menu_handler)
		self.application.add_handler(button_handler)

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

	async def process_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Process text messages and pass them to the central_controller.
		"""
		user_input = update.message.text  # Get the user's input

		self.message_metadata = {
			"update": update,
			"context": context
		}

		# Pass the message to the message queue (to be processed by the central_controller)
		self.recieve_message(user_input)
		

	def send_message(self, message, in_response_to):
		"""
		Send a message to the Telegram chat.
		"""
		print(f"Sending message: {message} (in response to: {in_response_to})")
		metadata = self.message_metadata[in_response_to]

		if(metadata is None):
			print(f"ERROR: Failed to respond to message \"{in_response_to}\"")
			return

		update = metadata["update"]
		context = metadata["context"]

		return_message = f"Received your command: '{in_response_to}'. Processing..."

		print("sending message")

		asyncio.run_coroutine_threadsafe(context.bot.send_message(
			chat_id=update.message.chat_id,
			text=return_message
		), self.loop)

	def await_message(self):
		"""
		Wait for a message from Telegram.
		This function is not used directly because Telegram handles events asynchronously.
		"""
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
