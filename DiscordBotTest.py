from DiscordBot import DiscordBot
import os
from dotenv import load_dotenv

#load the key from the env file
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_KEY")

#instantiate the discord bot
bot: DiscordBot = DiscordBot(DISCORD_TOKEN)