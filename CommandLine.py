from MessageService import MessageService

class CommandLine(MessageService):
    def __init__(self):
        super().__init__()
        self.is_ready = True
    def run_service(self):
        self.await_commands = True
        while self.await_commands:
            self.recieve_message(self.await_message())

    async def stop_service(self):
        self.await_commands = False

    def await_message(self):
        # Right now, theres a problem with threading where, when the input is expecting a string but
        #   thread gets killed it will throw an error. From what I can tell there's no good way to fix
        #   this.
        return input(f"Enter a message/command: ")
    
    def send_message(self, message):
        print(message)        
        return