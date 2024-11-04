from HomeAssistantController import HomeAssistantController

class CommandProcessor:
    """
    The CommandProcessor will be able to parse string inputs and resolve them into commands.
    It holds entity_mapping and action_mapping dictionaries, each hold human-readable strings and
    map them to HomeAssistant-readable strings.
    Use parse_command to convert command strings.
    """

    def __init__(self):
        # Dictionary to map target entities to Home Assistant entity IDs
        self.entity_mapping = {
            "all": "all",
            # Lock Dictionary
            "front door": "lock.front_door",
            "garage door": "lock.garage_door",
            # Light Dictionary
            "living room": "light.living_room"
        }

        # Dictionary to map actions to Home Assistant services
        self.action_mapping = {
            # Lock Dictionary
            "lock": "lock/lock",
            "unlock": "lock/unlock", 
            "open": "lock/open",
            # Light Dictionary
            "turn on": "light/turn_on",
            "toggle": "light/toggle"
        }
    
    def process_command(self, command):
        """
        Process a string command and convert it to a action_url and entity_id tuple.
        Parameters:
        command (string): The entire string command from the messaging services.

        Returns:
        (string, string): The action_url and entity_id tuple
        """
        command = command.lower()

        action = None
        for word in self.action_mapping:
            if word in command:
                action = word
                break
                
        target = None
        for entity in self.entity_mapping:
            if entity in command:
                target = entity
                break
        
        if(action and target):
            return (self.action_mapping[action], self.entity_mapping[target])
        else:
            if not action:
                action =  "Unrecognized action."
            if not target:
                target = "Unrecognized target."

        return "action_url", "ID_012345"