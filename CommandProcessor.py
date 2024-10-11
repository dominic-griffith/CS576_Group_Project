import os
import requests
from dotenv import load_dotenv

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

    if action and target:
        # The endpoint for the service call (e.g., turning on a light)
        service_call_url = f"{home_assistant_url}/api/services/{action_mapping[action]}"
        entity_id = entity_mapping[target]

        # Headers including the authorization token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Data to be sent with the service call (e.g., entity ID of the light)
        data = {
            "entity_id": entity_id
        }

        # Sending the POST request to the service call endpoint
        response = requests.post(service_call_url, headers=headers, json=data)

        # Check the response and return the result
        if response.status_code == 200:
            print(f"Success! The command '{action} {target}' was executed.")
        else:
            print(f"Failed to execute '{action} {target}':", response.status_code, response.text)
    else:
        # Handle invalid or unrecognized commands
        # Send to LLM
        if not action:
            print("Unrecognized action.")
        if not target:
            print("Unrecognized target.")



while True:
    user_command = input(f"Enter a command {{action}} {{target}} (or type 'exit' to quit): ")
    if user_command.lower() == "exit":
        print("Exiting...")
        break
    process_command(user_command)
