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

# The endpoint for the service call (e.g., turning on a light)
service_call_url = f"{home_assistant_url}/api/services/lock/unlock"

# Headers including the authorization token
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Data to be sent with the service call (e.g., entity ID of the light)
data = {
    "entity_id": "lock.front_door"
}

# Sending the POST request to the service call endpoint
response = requests.post(service_call_url, headers=headers, json=data)

# Checking the response
if response.status_code == 200:
    print("Success!")
else:
    print("Failed:", response.status_code, response.text)
