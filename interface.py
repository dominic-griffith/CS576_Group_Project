import tkinter as tk
from tkinter import ttk
import threading
import sys


class InterfaceManager:
    def __init__(self, service_manager, command_processor):
        self.service_manager = service_manager
        self.command_processor = command_processor
        self.root = tk.Tk()
        self.root.title("Home Assistant Interface")
        self.root.geometry("800x600")

        self.output_text = None
        self.user_input = None

        self._setup_ui()
        self._redirect_print()

    def _setup_ui(self):
        # Create a container for tabs
        tab_control = ttk.Notebook(self.root)

        # Console tab
        console_tab = ttk.Frame(tab_control)
        tab_control.add(console_tab, text="Console")

        # Dynamically create tabs for each service
        for service_name in self.service_manager.config["supported_services"]:
            service_tab = self._create_service_tab(tab_control, service_name)
            tab_control.add(service_tab, text=service_name.capitalize())

        tab_control.pack(expand=1, fill="both")

        # Console output
        output_frame = tk.Frame(console_tab, bg="lightgray", height=400)
        output_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(output_frame, state="normal", wrap="word")
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Console input
        input_frame = tk.Frame(console_tab)
        input_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.user_input = tk.Entry(input_frame)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)

        send_button = tk.Button(input_frame, text="Send", command=self.send_command)
        send_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def _create_service_tab(self, parent, service_name):
        frame = ttk.Frame(parent)
        ttk.Label(frame, text=f"Log in to {service_name.capitalize()}", font=("Calibri", 15)).pack(pady=8)

        ttk.Label(frame, text="Insert API Key:").pack(anchor=tk.W, padx=10)
        api_key_entry = ttk.Entry(frame, width=55)
        api_key_entry.pack(padx=10, pady=5)

        def save_api_key():
            api_key = api_key_entry.get()
            if api_key.strip():
                # Save the API key to the ServiceManager's config
                self.service_manager.config["services"][service_name]["api_key"] = api_key
                self.service_manager.save_config()
                print(f"{service_name.capitalize()} API key saved: {api_key}")
            else:
                print(f"Error: {service_name.capitalize()} API key cannot be empty.")

        ttk.Button(frame, text="Save", command=save_api_key).pack(pady=10)
        return frame

    def send_command(self):
        command = self.user_input.get()
        if command.strip():
            try:
                action, entity = self.command_processor.process_command(command)
                print(f"Processed Command -> Action: {action}, Entity: {entity}")
            except Exception as e:
                print(str(e))
        else:
            print("Error: Command cannot be empty.")
        self.user_input.delete(0, tk.END)

    def _redirect_print(self):
        class PrintRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget

            def write(self, message):
                self.text_widget.insert(tk.END, message)
                self.text_widget.see(tk.END)

            def flush(self):
                pass

        sys.stdout = PrintRedirector(self.output_text)

    def start(self):
        threading.Thread(target=self.root.mainloop, daemon=True).start()


if __name__ == "__main__":
    from services.service_manager import ServiceManager
    from command_processor import CommandProcessor

    # Initialize ServiceManager and CommandProcessor
    service_manager = ServiceManager()
    service_manager.load_config()
    service_manager.load_services()

    command_processor = CommandProcessor()

    # Create and start the interface
    interface = InterfaceManager(service_manager, command_processor)
    interface.start()
