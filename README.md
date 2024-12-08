# HomeAssistantHub

HomeAssistantHub is a Python-based application that bridges HomeAssistant with Discord and Telegram, allowing you to perform HomeAssistant actions through these platforms.

## Features

- Control HomeAssistant devices via Discord and Telegram.
- Receive notifications from HomeAssistant on Discord and Telegram.
- Easy setup and configuration.

## Requirements

- Python 3.10
- HomeAssistant
- Discord and Telegram accounts
- API Keys for all services

## Installation

1. Clone the repository and make it your working directory:

   ```bash
   git clone https://github.com/yourusername/HomeAssistantHub.git
   cd HomeAssistantHub
   ```

2. Create and activate a Python virtual environment:

   ```bash
   python3.10 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration
HomeAssistantHub has an interface that allows you to modify the configuration safely. It is recommended that you make changes there, however you can still make configuration changes manually with the following steps:

1. HomeAssistantHub uses configuration files at:
    ```bash
    ~/HomeAssistantHub/service_manager.json
    ```
    Where ~ stands for your users home directory. The config file is only created after first startup, so make sure the program has ran at least once.

2. Add your HomeAssistant, Discord, and Telegram credentials and settings to `service_manager.json` file. Here is an example configuration:

   ```json
    {
        "supported_services": [
            "home_assistant",
            "discord",
            "telegram" // Remove this if you don't want buggy telegram behavior
        ],
        "services": {
            "home_assistant": {
                "url": "your_home_assistant_url",
                "api_key": "api_key"
            },
            "discord": {
                "api_key": "api_key",
                "authorized_users": [
                    "authorizedUser1",
                    "authorizedUser2"
                ]
            },
            "telegram": {
                "api_key": "api_key"
            }
        }
    }
   ```

## Usage

1. Run the application:

   ```bash
   python central_controller.py
   ```

2. Depending on which message services you have configured, you will have multiple options for interacting with HomeAssistantHub. If none are configured, you can still send messages via the interfaces integrated command line; otherwise you can send messages to the bot you've configured to perform actions.

3. Ask HomeAssistantHub to perform actions like `Can you unlock the front door` and it will attempt to fulfill the request. HAH will check that it has an entity id for the front door's lock, and attempt to perform the lock/unlock action on it.
