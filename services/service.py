# Abstract classes: https://www.godaddy.com/resources/news/python-metaclasses

import threading
from abc import abstractmethod, ABC

class Service(ABC):
	"""
	A Service is an object that requires some kind of external tokens, like logins, keys, or urls.
	The service can either be threaded or run on the main thread, defined by is_threaded in the
	  constructor.
	"""

	def __init__(self, is_threaded):
		"""
		Initialize the service.

		Parameters:
		is_threaded (bool): Should this service be run in it's own thread?
		"""
		self.is_threaded = is_threaded

		if(is_threaded):
			self.thread = threading.Thread(target=self.run_service)

	@abstractmethod
	def load_config(self, config):
		"""
		Load configuration for this message service, the config will be passed from the
		  service_manager's config file and should contain everything the service needs to run.
		See home_assistant#load_config for example usage.
		  
		Parameters:
		config (dict): Dictionary holding important objects to the service, like API keys.

		Returns:
		bool, string: Config load success status, a string detailing problem if any.
		"""
		pass

	@abstractmethod
	def run_service(self):
		"""
		This is the method that will be targeted by the thread. Initialize the message service here
		  and it will be started by the central controller.

		Returns:
		void
		"""
		pass

	@abstractmethod
	def stop_service(self):
		"""
		This method must revert whatever happens in run_service to be used in properly shutting down
		  each thread.

		Returns:
		void
		"""
		pass
