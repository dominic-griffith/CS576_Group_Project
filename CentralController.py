import os
from dotenv import load_dotenv

from HomeAssistantController import HomeAssistantController
from CommandProcessor import CommandProcessor
from CommandLine import CommandLine

# This file is the central controller for the project, this should run the entire program

print()

#region Message services
message_services = {}

# TODO: Load message services from configuration file

if(len(message_services) == 0):
    print("Failed to load any message services. Adding a command line.")
    message_services["cmdline"] = CommandLine()

print(f"Loaded {len(message_services)} message service(s).")
#endregion

#region HomeAssistant controller
# TODO: Load homeassistant instance from configuration file/via message service

# Load environment variables from .env file
load_dotenv()

# Get the Home Assistant URL and Access Token from environment variables
home_assistant_url = os.getenv("HOME_ASSISTANT_URL")
access_token = os.getenv("HOME_ASSISTANT_TOKEN")

assert home_assistant_url is not None
assert access_token is not None

ha_controller = HomeAssistantController(home_assistant_url, access_token)

if(ha_controller is None):
    print("Failed to load HomeAssistant controller. Exiting.")
    exit()

print("Loaded HomeAssistant instance.")
#endregion

print("Starting...")

cmd_processor = CommandProcessor()

# Start each MessageService
for message_service in message_services.values():
    message_service.thread.start()

running = True
while running:
    for message_service in message_services.values():
        queue = message_service.message_queue

        if(len(queue) == 0):
            continue

        message_in = queue.pop(0).lower()

        if message_in == "exit":
            print("Exiting...")
            running = False
            break

        processed_cmd = cmd_processor.process_command(message_in)
        if(isinstance(processed_cmd, str)):
            message_service.send_message(f"Failed to process command \"{message_in}\": {processed_cmd}")
            continue

        print(f"Making request for action label {processed_cmd[0]} and entity id {processed_cmd[1]}")

        ha_controller.make_request(processed_cmd[0], processed_cmd[1])
        
        message_service.send_message(f"Recieved \"{message_in}\"")

# Stop each MessageService
for message_service in message_services.values():
    message_service.thread.join()