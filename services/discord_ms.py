import asyncio

#use messages to give info about status of devices
from discord import Intents, Client, Message, Embed, File, User

#use files or embeds to potentially add picture when requested
from discord import Message, Embed, File

## project files
from services.message_service import MessageService

#TODO make sure that discord is installed with the command:
#   pip install discord.py

class DiscordBot(MessageService):
	"""
	The DiscordBot leverages Discord's free messaging system to provide a method
		for users to access the HomeAssistant service

	TODO need to figure how this will scale. As of now, we only need 1 bot instance.
		It's important to think about how this will scale for many users, though
	"""

	def __init__(self):
		super().__init__()
		# A dictionary of string messages and the userMessage object associated with it, we can use
		#   this in send_message along with the "in_response_to" variable to access the incoming
		#   userMessage object
		self.message_metadata = {}
		self.authorized_users = {}

	def load_config(self, config):
		# load the api key from the configuration file
		# need an api key in order to startup a bot
		if(not "api_key" in config.keys()):
			return False, "No API Key provided."
		api_key = config["api_key"]
		if(api_key is None or len(api_key) == 0):
			return False, "Invalid API key provided."
		self.token = api_key

		# load in the list of authorized users from the configuration file
		# only authorized users can modify the state of a device, emphasizing a more secure home assistant
		if(not "authorized_users" in config.keys()):
			return False, ("There is currently no authorized users list in the config file. Configure this first (An empty list is fine).")
		# make it into a set to remove duplicates. emphasizes better efficiency when validating a user
		self.authorized_users = set(config["authorized_users"])

		return True, []

	def run_service(self):
		print("Starting discord bot...")
		# establish bot intents
		# bot should be able to read/send messages, but elevated privileges are not necessary
		print("\testablishing intents and client...", end="\t")
		botIntents: Intents = Intents.default()
		botIntents.message_content = True
		botIntents.messages = True
		self.intents = botIntents
		# if we decide to use a prefix for the bot commands, would set it here
		self.bot = Client(intents=self.intents)
		print("established.")

		# set up event handlers
		print("\tsetting event handlers...", end="\t\t")
		# event: bot logs in using api token
		self.bot.event(self.on_ready)
		# event: incoming message
		self.bot.event(self.on_message)
		print("\tcreated.")

		print("\tEstablishing connection...\t")
		try:
			#connect with token
			self.bot.run(self.token)
		except:
			print("unable to establish connection. please try again later.")

	def stop_service(self):
		asyncio.run_coroutine_threadsafe(self.bot.close(), self.bot.loop)

	## Login as the bot using the key
	# entry point for the bot; after logging in, bot can accept incoming messages
	async def on_ready(self):
		print(f"\nLogged in as {self.bot.user}.\n")
		self.is_ready = True

	## Respond to an incoming message, performing the corresponding operation
	async def on_message(self, user_msg):
		# We don't want to process the outgoing bot messages.
		if user_msg.author == self.bot.user:
			return

		# separate the message into its content and author
		msg_content = user_msg.content
		msg_author = user_msg.author

		# Store message metadata for when the program is ready to respond
		self.message_metadata[msg_content] = user_msg
		self.last_message = user_msg

		# print message; not necessary, just used to illustrate
		print(f"Received discord message from {msg_author}: {msg_content}")

		# validate the id of the user that just sent a message.
		# only authorized users should be able to modify the state of a device
		if msg_author.name not in self.authorized_users:
			# notify user that they are not authorized. do not process the command further.
			self.send_message(f"Sorry <@{msg_author.id}>, you are not authorized to do that.", msg_content)
			return

		# Recieve the message as a message service
		self.recieve_message(msg_content)

	### Abstract Class Functions
	# Not implementing await message since discord.py has the on_message event callback
	def await_message(self):
		return

	# Send a message back to the discord chat
	def send_message(self, message, in_response_to):
		userMessage = self.last_message
		if(in_response_to in self.message_metadata):
			userMessage = self.message_metadata[in_response_to]

		if(userMessage is None):
			print(f"ERROR: Failed to respond to message \"{in_response_to}\"")
			return

		asyncio.run_coroutine_threadsafe(userMessage.channel.send(message), self.bot.loop)