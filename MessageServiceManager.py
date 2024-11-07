import os

from CommandLine import CommandLine
from DiscordBot import DiscordBot

def load_services():
    message_services = {}

    # TODO: Load message services from configuration file

    # Manually load discord
    discord_key = os.getenv("DISCORD_KEY")

    assert discord_key is not None

    message_services["discord"] = DiscordBot(discord_key)

    # Load a command line message service if we don't have any others.
    if(len(message_services) == 0):
        print("Failed to load any message services. Adding a command line.")
        message_services["cmdline"] = CommandLine()

    print(f"Loaded {len(message_services)} message service(s).")
    return message_services

def start_services(message_services):
    # Start each MessageService
    for message_service in message_services.values():
        message_service.thread.start()

def stop_services(message_services):
    # Stop each MessageService
    for message_service in message_services.values():
        print(f"Stopping message service: {type(message_service)}")
        message_service.stop_service()

    # Stop each MessageService thread
    for message_service in message_services.values():
        message_service.thread.join()