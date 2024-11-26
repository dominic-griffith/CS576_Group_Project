import os
import requests

from services.service import Service

def load_home_assistant():
	# TODO: Load homeassistant instance from configuration file/via message service

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
	return ha_controller

class HomeAssistantController(Service):
	"""
	This class will be the way our program controls HomeAssistant, we should provide functionality here
	  for the rest of the program to access HomeAssistant.
	"""
	def __init__(self):
		super().__init__(False)

	def load_config(self, config):
		if(not "url" in config.keys()):
			return False, "No URL provided."
		url = config["url"]
		if(url is None or len(url) == 0):
			return False, "Invalid URL provided."
		if(not "api_key" in config.keys()):
			return False, "No API Key provided."
		api_key = config["api_key"]
		if(api_key is None or len(api_key) == 0):
			return False, "Invalid API key provided."

		self.ha_url = config["url"]
		self.long_term_key = config["api_key"]
		
		self.headers = {
			"Authorization": f"Bearer {self.long_term_key}",
			"Content-Type": "application/json"
		}
		return True, ""

	def run_service(self): # HA controller doesn't use these methods
		return
	
	def stop_service(self): # HA controller doesn't use these methods
		return

	def make_request(self, action_url, entity_id):
		"""
		Make a request to the HomeAssistant instance.
		Parameters:
		action_label (string): the end of the service_call_url, labeling the action to be performed.
		i.e. ha_url/api/services/<action_label>
		entity_label (string): the HomeAssistant entity id
		i.e. lock.front_door

		Returns:
		bool: Request success status
		"""

		service_call_url = f"{self.ha_url}/api/services/{action_url}"
		data = {
			"entity_id": entity_id
		}

		# Sending the POST request to the service call endpoint
		response = requests.post(service_call_url, headers=self.headers, json=data)

		return (response.status_code == 200, response.text)

	def get_all_entities(self):
		"""
		Retrieves all entities from the Home Assistant instance.

		Returns:
		list: A list of dictionaries containing information about each entity.
		
		Raises:
		requests.exceptions.RequestException: If there is an issue with the HTTP request.
		"""

		url = f"{self.ha_url}/api/states"
		response = requests.get(url, headers=self.headers)
		response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
		return response.json()