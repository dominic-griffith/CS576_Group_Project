import sys
import signal

from services.service_manager import ServiceManager
from command_processor import CommandProcessor, CommandProcessingError
from services.message_service import MessageService
from interface import InterfaceManager

# This file is the central controller for the project, this should run the entire program

# Load core objects
service_manager = ServiceManager()

# Load services
service_manager.load_config()
service_manager.load_services()

ha_controller = None
if('home_assistant' in service_manager.services.keys()):
    ha_controller = service_manager.services["home_assistant"]

if(ha_controller is None):
    print("WARNING: HomeAssistant hasn't loaded, no requests will be made.")

if('telegram' in service_manager.services.keys()):
    print("WARNING: Telegram isn't supported, expect broken behavior.")

if(len(service_manager.get_message_services()) == 0):
    service_manager.load_service("command_line")

cmd_processor = CommandProcessor(ha_controller)

# Create and load custom commands
def stop_running():
    global running
    running = False

    return {"msg": "Exiting HomeAssistantHub."}

def get_entity_list():
    json = ha_controller.get_all_entities()
    entity_ids = [item["entity_id"] for item in json]

    return {"msg": entity_ids}

cmd_processor.add_custom_command("exit", stop_running)
cmd_processor.add_custom_command("listdevices", get_entity_list)

# Start
# Load interface
interface = InterfaceManager(service_manager, cmd_processor)

class PrintRedirector:
    def __init__(self, orig_out, interface):
        self.orig_out = orig_out
        self.interface = interface

    def write(self, message):
        self.interface.console_queue.append(message)
        self.orig_out.write(message)

    def flush(self):
        pass

sys.stdout = PrintRedirector(sys.stdout, interface)

# Start program
print("Starting...")

service_manager.start_services()

running = True

# Establish signal handler for Ctrl+C support
def signal_handler(sig, frame):
    stop_running()

signal.signal(signal.SIGINT, signal_handler)

try:
    print("Running...")
    while running:
        interface.update()

        # Loop through each message service and check if its queue has pending messages for us to
        #   handle.
        for message_service in service_manager.get_message_services():
            queue = message_service.message_queue

            # If there are no messages in queue, continue
            if(len(queue) == 0):
                continue

            # Get the first available message
            message_in = queue.pop(0).lower()

            # Try to process command, if we can't handle the error that it throws.
            process_result = None
            try:
                process_result = cmd_processor.process_command(message_in)
            except CommandProcessingError as e:
                message_service.send_message(f"Failed to process command \"{message_in}\": {e.message}", message_in)
                print(e)
                continue

            if(process_result["processed_type"] == "ha_cmd"):

                action_label = process_result["action_label"]
                entity_id = process_result["entity_id"]

                # Debug log message
                print(f"Processed HomeAssistant command {'with SLM' if process_result['used_slm'] else 'manually'} as action label {action_label} and entity id {entity_id}")

                # Make the request for HomeAssistant
                request_status, request_response_text = True, None
                if(ha_controller is not None):
                    try:
                        request_status, request_response_text = ha_controller.make_request(action_label, entity_id)
                    except Exception as e:
                        request_status = False
                
                print(f"{'Successfully made' if request_status else 'Failed to make'} request to HomeAssistant. Response: {request_response_text}")

                # Output message to user via message_service
                return_message = None
                if(request_status):
                    return_message = f"Recieved \"{message_in}\" and {'the slm' if process_result['used_slm'] else 'manually'} performed {action_label} on {entity_id}"
                else:
                    return_message = f"HomeAssistant failed to perform the request: {'No response.' if request_response_text is None else request_response_text}"

                message_service.send_message(return_message, message_in)

            elif(process_result["processed_type"] == "custom_cmd"):
                
                message_service.send_message(f"Recieved command \"{process_result['custom_cmd_label']}\"", message_in)
                cmd_exec = process_result["custom_cmd"]()
                if("msg" in cmd_exec):
                    message_service.send_message(cmd_exec["msg"], message_in)

                print(f"Concluded request for custom command \"{process_result['custom_cmd_label']}\"")


finally:
    print("Shutting down...")
    service_manager.stop_services()