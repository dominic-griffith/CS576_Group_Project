import signal
from dotenv import load_dotenv

from services.service_manager import ServiceManager
from command_processor import CommandProcessor, CommandProcessingError
from services.message_service import MessageService

# This file is the central controller for the project, this should run the entire program

# Load environment variables from .env file
load_dotenv()

# Load core objects
service_manager = ServiceManager()
cmd_processor = CommandProcessor()

service_manager.load_config()
service_manager.load_services()

ha_controller = None
if('home_assistant' in service_manager.services.keys()):
    ha_controller = service_manager.services["home_assistant"]

if(ha_controller is None):
    print("WARNING: HomeAssistant hasn't loaded, no requests will be made.")

if(len(service_manager.get_message_services()) == 0):
    service_manager.load_service("command_line")

print("Starting...")

service_manager.start_services()

running = True

# Establish signal handler for Ctrl+C support
def signal_handler(sig, frame):
    global running
    running = False

signal.signal(signal.SIGINT, signal_handler)

try:
    print("Running...")
    while running:
        # Loop through each message service and check if its queue has pending messages for us to
        #   handle.
        for message_service in service_manager.get_message_services():
            queue = message_service.message_queue

            # If there are no messages in queue, continue
            if(len(queue) == 0):
                continue

            # Get the first available message
            message_in = queue.pop(0).lower()

            # If the message is exit, exit the program
            # TODO: This probably should be handled better. Thinking of how, will change eventually.
            if(message_in == "exit"):
                print("Exiting...")
                running = False
                break

            # Try to process command, if we can't handle the error that it throws.
            try:
                action_label, entity_id = cmd_processor.process_command(message_in)
            except CommandProcessingError as e:
                message_service.send_message(f"Failed to process command \"{message_in}\": {e.message}", message_in)
                print(e)
                continue

            # Debug log message
            print(f"Making request for action label {action_label} and entity id {entity_id}")

            # Make the request for HomeAssistant
            request_status, request_response_text = True, None
            if(ha_controller is not None):
                request_status, request_response_text = ha_controller.make_request(action_label, entity_id)
            
            # Output message to user via message_service
            if(request_status):
                message_service.send_message(f"Recieved \"{message_in}\"", message_in)
            else:
                message_service.send_message(f"HomeAssistant failed to perform the request: {request_response_text}")

finally:
    print("Shutting down...")
    service_manager.stop_services()