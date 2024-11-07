import signal
from dotenv import load_dotenv

from HomeAssistantController import load_home_assistant
from MessageServiceManager import load_services, start_services, stop_services
from CommandProcessor import CommandProcessor, CommandProcessingError

# This file is the central controller for the project, this should run the entire program

# Load environment variables from .env file
load_dotenv()

# Load core objects
ha_controller = load_home_assistant()
message_services = load_services()
cmd_processor = CommandProcessor()

print("Starting...")
start_services(message_services)

tick_count = 0
running = True

# Establish signal handler for Ctrl+C support
def signal_handler(sig, frame):
    global running
    running = False

signal.signal(signal.SIGINT, signal_handler)

try:
    while running:
        for message_service in message_services.values():
            if(not message_service.is_ready and tick_count % 1000 == 0):
                # print(f"Service {type(message_service)} is not ready")
                continue

            queue = message_service.message_queue
            # if(tick_count % 1000 == 0):
            #     print(f"Service {type(message_service)} has queue len {len(queue)}")

            if(len(queue) == 0):
                continue

            message_in = queue.pop(0).lower()

            if message_in == "exit":
                print("Exiting...")
                running = False
                break

            try:
                processed_cmd = cmd_processor.process_command(message_in)
            except CommandProcessingError as e:
                message_service.send_message(f"Failed to process command \"{message_in}\": {e.message}")
                print(e)
                continue

            print(f"Making request for action label {processed_cmd[0]} and entity id {processed_cmd[1]}")

            ha_controller.make_request(processed_cmd[0], processed_cmd[1])
            
            message_service.send_message(f"Recieved \"{message_in}\"", message_in)
        tick_count += 1
finally:
    print("Shutting down...")
    stop_services(message_services)