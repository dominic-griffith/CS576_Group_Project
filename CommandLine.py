from MessageService import MessageService

class CommandLine(MessageService):
    def _recieve_message(self):
        return input(f"Enter a message/command: ")
    
    def send_message(self, message):
        print(message)        
        return