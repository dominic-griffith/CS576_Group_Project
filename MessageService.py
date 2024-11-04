# Python is a garbage language: https://www.godaddy.com/resources/news/python-metaclasses

from abc import abstractmethod, ABC
import threading

class MessageService(ABC):
    """
    A MessageService can receive messages and send messages. Received messages come from the user
      and sent messages are sent to the user.
    The message_queue should be used to read incoming messages.
    """

    def __init__(self):
        self.message_queue = []
        self.thread = threading.Thread(target=self._recieve_message_clock)
        # self.thread.start()

    def _recieve_message_clock(self):
        while True:
            self.message_queue.append(self._recieve_message())

    @abstractmethod
    def _recieve_message(self):
        """
        Receive a message from this message service. This shouldn't be called outside the
          MessageService class, it is called internally. Messages should be read from the
          message_queue.

        Returns:
        string: The message received from the message service, will be added to the message queue
        """
        pass

    @abstractmethod
    def send_message(self, message):
        """
        Send a message to this message service
        """
        pass

    