from slm_command_processor import SLMCommandProcessor

class CommandProcessor:
    """
    The CommandProcessor will be able to parse string inputs and resolve them into commands.
    It holds entity_mapping and action_mapping dictionaries, each hold human-readable strings and
    map them to HomeAssistant-readable strings.
    Use parse_command to convert command strings.
    """

    def __init__(self):
        self.slm_processor = SLMCommandProcessor()

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

        self.custom_commands = {}
    
    def add_to_enity_mapping(self, entity_name, entity_id):
        #Validate the entity_id is valid with HomeAssistant
        self.entity_mapping[entity_name] = entity_id
    
    def add_to_action_mapping(self, action_name, action_id):
        #Validate the action_id is valid with HomeAssistant
        self.action_mapping[action_name] = action_id

    def add_custom_command(self, command_name, command):
        self.custom_commands[command_name] = command

    def remove_from_entity_mapping(self, entity_name):
        if entity_name in self.entity_mapping:
            del self.entity_mapping[entity_name]
            return True
        else:
            return False
        
    def remove_from_action_mapping(self, action_name):
        if action_name in self.action_mapping:
            del self.action_mapping[action_name]
            return True
        else:
            return False
    
    def process_command(self, command):
        """
        Process a string command and convert it to a action_url and entity_id tuple.
        Parameters:
        command (string): The entire string command from the messaging services.

        Returns:
        (string, string): The action_url and entity_id tuple
        """
        command = command.lower()
        command_split = command.split(" ")

        # Theres 3 major steps: Parse as custom command, parse as home assistant command, parse with slm
        # 1. Try to parse as custom command first
        if(command_split[0] in self.custom_commands):
            return {
                "processed_type": "custom_cmd",
                "custom_cmd": self.custom_commands[command_split[0]],
                "custom_cmd_label": command_split[0]
            }

        # 2. Try to parse as HomeAssistant command
        # Sort actions by length to prevent partial matches (e.g. "lock" being matched before "unlock")
        sorted_actions = sorted(self.action_mapping.keys(), key=len, reverse=True)

        action = None
        for word in sorted_actions:
            if word in command:
                action = word
                break
                
        target = None
        for entity in self.entity_mapping:
            if entity in command:
                target = entity
                break
        
        # Successfully processed the command without SLM, return the parse result
        # We want this to happen before the SLM because it is 100% what the user intends to do.
        # That way, if the user's SLM inputs aren't what they want, they can use the consistent commands
        if(action and target):
            return {
                "processed_type": "ha_cmd",
                "used_slm": False,
                "action_label": self.action_mapping[action],
                "entity_id": self.entity_mapping[target]
            }

        # 3. Parse with SLM
        # TODO: Needs to return entity_id and action_label. If it's easier for the SLM, we could make it output a key from the action_mapping dictionary (like "lock" "unlock")
        entity_id = self.slm_processor.generate_api_command(command)
        action_label = "lock/lock"
        if(action_label and entity_id):
            print(f"SLM processed command: {entity_id} {action_label}")
            return {
                "processed_type": "ha_cmd",
                "used_slm": True,
                "action_label": action_label,
                "entity_id": entity_id
            }

        if not action:
            raise CommandProcessingError("Unrecognized action.")
        if not target:
            raise CommandProcessingError("Unrecognized target.")
            
class CommandProcessingError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
    
    def __str__(self):
        return f"Failed to process command: {self.message}"
