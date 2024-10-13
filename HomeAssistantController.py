import requests

"""
This class will be the way our program controls HomeAssistant, we should provide functionality here
  for the rest of the program to access HomeAssistant.
"""
class HomeAssistantController:
    def __init__(self, api_url, api_key):
        self.ha_url = api_url
        self.long_term_key = api_key

    """
    Make a request to the HomeAssistant instance.
    Parameters:
    action_label (string): the end of the service_call_url, labeling the action to be performed.
      i.e. ha_url/api/services/<action_label>
    entity_label (string): the HomeAssistant entity id
      i.e. lock.front_door
    """
    def make_request(self, action_label, entity_label):
        # The endpoint for the service call (e.g., turning on a light)
        service_call_url = f"{self.ha_url}/api/services/{action_label}"

        # Headers including the authorization token
        headers = {
            "Authorization": f"Bearer {self.long_term_key}",
            "Content-Type": "application/json"
        }

        # Data to be sent with the service call (e.g., entity ID of the light)
        data = {
            "entity_id": entity_label
        }

        # Sending the POST request to the service call endpoint
        response = requests.post(service_call_url, headers=headers, json=data)

        # Check the response and return the result
        if response.status_code == 200:
            print(f"Success! The command '{action_label} {entity_label}' was executed.")
        else:
            print(f"Failed to execute '{action_label} {entity_label}':", response.status_code, response.text)

    """
    Retrieves all entities from the Home Assistant instance.

    Returns:
    list: A list of dictionaries containing information about each entity.
    
    Raises:
    requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """
    def get_all_entities(self):
        url = f"{self.api_url}/api/states"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()