import os
import requests
from dotenv import load_dotenv
from HomeAssistantController import HomeAssistantController

# Load environment variables from .env file
load_dotenv()

# Get the Home Assistant URL and Access Token from environment variables
home_assistant_url = os.getenv("HOME_ASSISTANT_URL")
access_token = os.getenv("HOME_ASSISTANT_TOKEN")

assert home_assistant_url is not None
assert access_token is not None

# Dictionary to map target entities to Home Assistant entity IDs
entity_mapping = {
    "all": "all",
    # Lock Dictionary
    "front door": "lock.front_door",
    "garage door": "lock.garage_door",
    # Light Dictionary
    "living room": "light.living_room"
}

# Dictionary to map actions to Home Assistant services
action_mapping = {
    # Lock Dictionary
    "lock": "lock/lock",
    "unlock": "lock/unlock", 
    "open": "lock/open",
    # Light Dictionary
    "turn on": "light/turn_on",
    "toggle": "light/toggle"
}

"""
Process a string command and convert it to a action_url and entity_id tuple.
Parameters:
command (string): The entire string command from the messaging services.

Returns:
(string, string): The action_url and entity_id tuple
"""
def process_command(command):
    command = command.lower()

    action = None
    for word in action_mapping:
        if word in command:
            action = word
            break
            
    target = None
    for entity in entity_mapping:
        if entity in command:
            target = entity
            break
    
    if(action and target):
        return (action_mapping[action], entity_mapping[target])
    else:
        if not action:
            return "Unrecognized action."
        if not target:
            return "Unrecognized target."

ha_controller = HomeAssistantController(home_assistant_url, access_token)
while True:
    user_command = input(f"Enter a command {{action}} {{target}} (or type 'exit' to quit): ")
    if user_command.lower() == "exit":
        print("Exiting...")
        break

    processed_cmd = process_command(user_command)
    if(processed_cmd is str):
        print(f"Failed to process command \"{user_command}\": {processed_cmd}")
        break

    print(f"Making request for action label {processed_cmd[0]} and entity id {processed_cmd[1]}")

    ha_controller.make_request(processed_cmd[0], processed_cmd[1])
