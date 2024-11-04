#used to detect whether a user wants to turn off or turn on a device (the VERB)
#TODO can probably turn this into a single dictionary with the keyword as the key, and the modified device state as the vale
# E.g. {"turn on": "on", "toggle": "toggle" "close":"turn off"
activation_keywords = ["turn on", "on", "activate", "enable", "start", "open", "lock"]
deactivation_keywords = ["off", "deactivate", "disable", "stop", "close", "unlck"]

#used to detect the device whose state is being modified
device_keywords = ["lights", "light", "timer", "door", "lock"]
