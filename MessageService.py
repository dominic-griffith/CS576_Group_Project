# Python is a garbage language: https://www.godaddy.com/resources/news/python-metaclasses

import threading
from abc import abstractmethod, ABC

class MessageService(ABC):
	"""
	A MessageService can receive messages and send messages. Received messages come from the user
	  and sent messages are sent to the user.
	The message_queue should be used to read incoming messages.
	"""
	
	def __init__(self):
		self.message_queue = []
		self.is_ready = False
		self.thread = threading.Thread(target=self.run_service)

	@abstractmethod
	def run_service(self):
		"""
		This is the method that will be targeted by the thread. Initialize the message service here
		  and it will be started by the central controller.

		Returns:
		void
		"""

	@abstractmethod
	async def stop_service(self):
		"""
		This method must revert whatever happens in run_service to be used in properly shutting down
		  each thread.

		Returns:
		void
		"""

	def recieve_message(self, message):
		"""
		Callback for when a message is recieved from a message service. Appends the string message
		  to the end of the message_queue to be picked up by the CentralController.

		Returns:
		void
		"""
		self.message_queue.append(message)

	@abstractmethod
	def await_message(self):
		"""
		Wait for a message from this message service. This shouldn't be called outside the
		  MessageService class, it is called internally. Messages should be read from the
		  message_queue.

		Returns:
		string: The message received from the message service, will be added to the message queue
		"""
		pass

	@abstractmethod
	def send_message(self, message, in_response_to):
		"""
		Send a message to this message service

		Returns:
		void
		"""
		pass