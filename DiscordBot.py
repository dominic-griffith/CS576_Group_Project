import os
from dotenv import load_dotenv

#use messages to give info about status of devices
from discord import Intents, Client, Message, Embed, File

#use files or embeds to potentially add picture when requested
from discord import Message, Embed, File

## project files
from MessageService import MessageService
from HomeAssistantController import HomeAssistantController
from CommandProcessor import CommandProcessor
from CommandLine import CommandLine

## device keywords
from DeviceKeywords import activation_keywords, deactivation_keywords, device_keywords

#TODO make sure that discord is installed with the command:
#   pip install discord.py

class DiscordBot(MessageService):
    """
    The DiscordBot leverages Discord's free messaging system to provide a method
        for users to access the HomeAssistant service

    TODO need to figure how this will scale. As of now, we only need 1 bot instance.
        It's important to think about how this will scale for many users, though
    """
    def __init__(self, TOKEN):
        print("Starting discord bot...")
        #create a queue to handle multiple incoming messages
        #should store (message, UID) tuples if multiple people are using the bot
        #TODO remove if not needed
        self.message_queue = []

        # create an object to process the commands from incoming messages
        print("\tcreating command processor...", end="\t\t")
        self.commandProcessor = CommandProcessor()
        print("created.")

        #create a new thread
        #self.thread = threading.Thread(target=self.recieve_message_clock)

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

        print("\tlogging in...")
        self.run(TOKEN)

    ## Start up bot
    ## Bot must be running before any incoming messages can be processed
    def run(self, TOKEN):
        print("\t\testablishing connection...\t")
        try:
            #connect with token
            self.bot.run(TOKEN)
        except:
            print("unable to establish connection. please try again later.")

    ## Login as the bot using the key
    # entry point for the bot; after logging in, bot can accept incoming messages
    async def on_ready(self):
        print(f"\nLogged in as {self.bot.user}.\n")

    ## Respond to an incoming message, performing the corresponding operation
    async def on_message(self, userMessage):
        # avoid letting the discord bot send a message in response to itself
        if userMessage.author == self.bot.user:
            return
        # send message back to channel
        await userMessage.channel.send(self.send_message(userMessage))

    ### Abstract Class Functions
    #TODO integrate with abstract class functions
    def _recieve_message(self):
        return

    # process commands corresponding to the message sent by the user
    # if command is incomprehensible, first contact the SLL and use that to get the command
    def send_message(self, userMessage):
        # set user id for author of message. can be used to validate devices
        userMessageAuthor = userMessage.author
        # get contents of message. type is a string
        userMessageContent = userMessage.content

        # print message; not necessary, just used to illustrate
        print(f"received message from @{userMessageAuthor}: {userMessageContent}")

        # process the message to perform the corresponding content
        # once the command is processed, return the response to on_message so the bot can respond
        print("handling command...")
        response = self.process_message(userMessageContent)

        return response


    #perform preprocessing on the message and perform the corresponding command
    def process_message(self, userMessageContent):
        #use booleans to see if a message is unintelligible
        found_noun = False
        found_verb = False

        ##TODO enhance command preprocessing - handle capitalization, keyword isolation, handle varying device types (e.g. lock vs light)
        userMessageContentLower = userMessageContent.lower()
        # by default, do not turn on devices
        # this ensures users utilites are not being wasted, and doors are not unlocked by default
        ##TODO can maybe pass flags to tell if a certain device is on
        modifiedDeviceState = "TURN OFF"

        ## TODO also need a way to detect location (eg. kitchen lights vs living room lights)
        # get device being modified
        # device is the noun we are looking for
        deviceBeingModified = "device"

        # search the incoming message for the device
        for keyword in device_keywords:
            if keyword in userMessageContentLower:
                deviceBeingModified = keyword
                found_noun = True
                break

        # TODO modify to handle different kinds of device (e.g. lock vs light)
        # search the incoming message to see how the device is being modified
        for keyword in activation_keywords:
            if keyword in userMessageContentLower:
                modifiedDeviceState = "TURN ON"
                found_verb = True
                break
        # if keyword to turn on device is not found, check if something is being turned off
        if not found_verb:
            for keyword in activation_keywords:
                if keyword in userMessageContentLower:
                    modifiedDeviceState = "TURN OFF"
                    found_verb = True
                    break

        #if we don't know how we're modifying the device, the message is unintelligible. contact the SLL
        if not found_verb:
            #contact_ssl(userMessageContentLower)
            print("unsure how to modify device. passing to SLL...")

        ##TODO add call to command processor
        messageForCommandProcessor = modifiedDeviceState+" "+deviceBeingModified
        print(f"\tpassing to command processor: {messageForCommandProcessor}...")
        (action_url, entity_id) = self.commandProcessor.process_command(messageForCommandProcessor)
        print("processed.")

        return f"{modifiedDeviceState} your {deviceBeingModified} (ID: {entity_id})."