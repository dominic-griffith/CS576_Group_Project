import os
import json

from services.home_assistant import HomeAssistantController
from services.message_service import MessageService
from services.command_line_ms import CommandLine
from services.discord_ms import DiscordBot
from services.telegram_ms import TelegramBot

def load_json(file_path):
    """
    Load JSON from a specific file path.

    Parameters:
    file_path (string): The file path to be loaded as json

    Returns:
    dict: The loaded json as a dictionary
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"No such file: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file: {file_path}")
        return None

def save_json(file_path, data):
    """
    Save JSON to a specific file path.

    Parameters:
    file_path (string): The file path to be saved to
    data (dict): The json dictionary to save to the file

    Returns:
    void
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"An error occurred while saving to the file: {e}")

# Default config if the local file doesn't exist
default_config = {
    "supported_services": ["home_assistant", "discord", "telegram"],
    "services": {
        "home_assistant": {
            "url": "",
            "api_key": ""
        },
        "discord": {
            "api_key": ""
        },
        "telegram": {
            "api_key": ""
        }
    }
}

class ServiceManager():
    """
    The ServiceManager will load all services used by the program, see Service for details.
    It will take the config file from ~/HomeAssistantHub/service_manager.json and try to load each
      service from supported_services. The supported_service names are translated to python objects
      via _init_service_by_name.
    Each service's config should have the relevant details pertaining to the service as that
      section will be passed to the service via load_config.
    """
    def __init__(self):
        # Initialize empty services dict
        self.services = {}

        # Load the location of the config json
        home_dir = os.path.expanduser('~')
        self.config_filepath = os.path.join(home_dir, "HomeAssistantHub", 'service_manager.json')

#region Config load/save
    def load_config(self):
        """
        Load the ServiceManager config, if the config doesn't exist it will load the default config
          and automatically save it.
        """
        # Load config from local file, there is a possibility it could be None
        self.config = load_json(self.config_filepath)

        # Load default config and save it for future use
        if(self.config is None):
            self.config = default_config
            self.save_config()

            print("Saved default config.")

    def save_config(self):
        """
        Save the ServiceManager config to its filepath.
        """
        # Save config_json to the loaded config filepath
        save_json(self.config_filepath, self.config)
#endregion

#region Loading/Starting/Stopping
    def load_services(self):
        """
        Load all services by the config's supported_services list, it enumaretes each string in
          the list and calls load_service on each one.
        """
        for service_name in self.config["supported_services"]:
            self.load_service(service_name)

        loaded_service_count = len(self.services.keys())
        if(loaded_service_count == 0):
            print("Didn't load any services. Have you configured ~/HomeAssistantHub/service_manager.json yet?")
        else:
            print(f"Loaded {loaded_service_count} service(s): {str.join(', ', self.services.keys())}")

    def load_service(self, service_name):
        """
        Load a specific service by service name.

        Parameters:
        service_name (string): The service name to be loaded.

        Returns:
        void, the loaded service will be placed in the ServiceManager#services dictionary.
        """

        # Initialize the service by it's name
        service = self._init_service_by_name(service_name)

        if(service is None):
            print(f"Failed to initialize service by name \"{service_name}\"")
            return
            
        # If the service's config section isn't in the main config, create an empty config
        if(not service_name in self.config["services"].keys()):
            self.config["services"][service_name] = {}

        # Load the config on the service and get the results
        cfg_load_result, cfg_load_problem = service.load_config(self.config["services"][service_name])

        # Show error if the service failed to load
        if(not cfg_load_result):
            print(f"Failed to load config for service \"{service_name}\": {cfg_load_problem}")
            return

        # Register the service with the ServiceManager
        self.services[service_name] = service

    def start_services(self):
        """
        Start all services in the service manager, if the service is threaded we will start its
          thread, if not, we just call run_service here.
        """
        for service in self.services.values():
            if(service.is_threaded):
                service.thread.start()
            else:
                service.run_service()

    def stop_services(self):
        """
        Stop all services in the service manager.
        """
        for service in self.services.values():
            print(f"Stopping service: {type(service)}")
            service.stop_service()

            if(service.is_threaded):
                service.thread.join()
#endregion

    def get_message_services(self):
        """
        Get all of the services that are children of the MessageService class.

        Returns:
        list<MessageService>: A list of all MessageServices.
        """
        return list(filter(lambda service: isinstance(service, MessageService), self.services.values()))

    def _init_service_by_name(self, name):
        """
        Utility function to load a service based on it's configuration name. Should only be called
          inside ServiceManager.

        Parameters:
        name (string): The config name of the service

        Returns:
        Service: The initialized service
        """
        if(name == "home_assistant"):
            return HomeAssistantController()
        elif(name == "command_line"):
            return CommandLine()
        elif(name == "discord"):
            return DiscordBot()
        elif(name == "telegram"):
            return TelegramBot()
        return None