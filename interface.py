'''
import tkinter as tk
from tkinter import ttk
from central_controller import service_manager  # Import the ServiceManager from the project
from command_processor import CommandProcessor

# Create CommandProcessor instance
command_processor = CommandProcessor()

def send_command():
    """Handle sending commands from the console input."""
    command = user_input.get()
    if command.strip():
        try:
            # Process the command and display the output
            response = command_processor.parse_command(command)
            display_output(f"Command: {command}\nResponse: {response}")
        except Exception as e:
            display_output(f"Error: {str(e)}")
    user_input.delete(0, tk.END)

def display_output(message):
    """Display a message in the console output."""
    console_output.config(state='normal')
    console_output.insert(tk.END, f"{message}\n")
    console_output.config(state='disabled')
    console_output.see(tk.END)

def create_service_tab(parent, service_name):
    """Create a login tab for a specific service."""
    frame = ttk.Frame(parent)
    ttk.Label(frame, text=f"Log in to {service_name}", font=("Arial", 12)).pack(pady=10)

    ttk.Label(frame, text="API Key:").pack(anchor=tk.W, padx=10)
    api_key_entry = ttk.Entry(frame, width=50)
    api_key_entry.pack(padx=10, pady=5)

    def save_api_key():
        """Save the entered API key."""
        api_key = api_key_entry.get()
        if api_key.strip():
            # Save API key to the service manager
            service_manager.load_service(service_name, api_key)
            display_output(f"{service_name} API key saved successfully!")
        else:
            display_output("API key cannot be empty.")

    ttk.Button(frame, text="Save", command=save_api_key).pack(pady=10)
    return frame

def create_interface():
    """Create the main interface."""
    root = tk.Tk()
    root.title("Home Assistant Interface")
    root.geometry("800x600")

    # Create a container for tabs
    tab_control = ttk.Notebook(root)

    # Console tab
    console_tab = ttk.Frame(tab_control)
    tab_control.add(console_tab, text="Console")

    # Home Assistant tab
    ha_tab = create_service_tab(tab_control, "HomeAssistant")
    tab_control.add(ha_tab, text="HomeAssistant")

    # Discord tab
    discord_tab = create_service_tab(tab_control, "Discord")
    tab_control.add(discord_tab, text="Discord")

    # Elimina la pestaña de Telegram
    tab_control.pack(expand=1, fill="both")

    # Layout for the Console tab
    global console_output
    output_frame = tk.Frame(console_tab, bg="lightgray", height=400)
    output_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    console_output = tk.Text(output_frame, state='disabled', wrap='word')
    console_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    global user_input
    input_frame = tk.Frame(console_tab)
    input_frame.pack(side=tk.BOTTOM, fill=tk.X)

    user_input = tk.Entry(input_frame)
    user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)

    send_button = tk.Button(input_frame, text="Send", command=send_command)
    send_button.pack(side=tk.RIGHT, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_interface()
'''
