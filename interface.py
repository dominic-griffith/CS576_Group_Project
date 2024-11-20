import tkinter as tk
from tkinter import ttk

def create_service_tab(parent, service):
    #create a tab (Console, HomeAssistant, Discord, Telegram)
    frame = ttk.Frame(parent)
    ttk.Label(frame, text=f"Log in to {service}", font=("Calibri", 15)).pack(pady=8)

    ttk.Label(frame, text="Insert API Key:").pack(anchor=tk.W, padx=10)
    api_key_entry = ttk.Entry(frame, width=55)
    api_key_entry.pack(padx=10, pady=5)

    def save_api_key():
        #save the entered API key
        api_key = api_key_entry.get()
        if api_key.strip():  #if api key is valid
            output_text.insert(tk.END, f"{service} API key saved: {api_key}\n")
        else:
            output_text.insert(tk.END, f"Error: {service} API key cannot be empty.\n")

    ttk.Button(frame, text="Save", command=save_api_key).pack(pady=10)
    return frame

def send_command():
    #handle user commands entered in the console
    command = user_input.get()
    if command.strip():
        output_text.insert(tk.END, f"Command sent: {command}\n")
    else:
        output_text.insert(tk.END, "Error: Command cannot be empty.\n")
    user_input.delete(0, tk.END)

def create_interface():
    root = tk.Tk()
    root.title("Home Assistant Interface")
    root.geometry("800x600")

    #create a container for tabs
    tab_control = ttk.Notebook(root)

    #Console tab
    console_tab = ttk.Frame(tab_control)
    tab_control.add(console_tab, text="Console")

    #Home Assistant tab
    ha_tab = create_service_tab(tab_control, "HomeAssistant")
    tab_control.add(ha_tab, text="HomeAssistant")

    #Discord tab
    discord_tab = create_service_tab(tab_control, "Discord")
    tab_control.add(discord_tab, text="Discord")

    #Telegram tab
    telegram_tab = create_service_tab(tab_control, "Telegram")
    tab_control.add(telegram_tab, text="Telegram")

    tab_control.pack(expand=1, fill="both")


    global output_text, user_input
    output_frame = tk.Frame(console_tab, bg="lightgray", height=400)
    output_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    output_text = tk.Text(output_frame, state='normal', wrap='word')
    output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    input_frame = tk.Frame(console_tab)
    input_frame.pack(side=tk.BOTTOM, fill=tk.X)

    user_input = tk.Entry(input_frame)
    user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)

    send_button = tk.Button(input_frame, text="Send", command=send_command)
    send_button.pack(side=tk.RIGHT, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_interface()
