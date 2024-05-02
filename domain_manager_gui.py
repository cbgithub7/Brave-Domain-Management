import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import domain_manager_functions as dm_functions

def on_add_button_click(event=None):
    domain = add_entry.get()
    if domain:
        result = dm_functions.add_domain(domain)
        update_feedback(result)
        refresh_existing_domains()

def on_remove_button_click():
    index = existing_domains_listbox.curselection()
    if index:
        result = dm_functions.remove_domain(existing_domains_listbox.get(index))
        update_feedback(result)
        refresh_existing_domains()

def on_refresh_button_click():
    refresh_existing_domains()
    update_feedback("List refreshed.")

def refresh_existing_domains():
    existing_domains_listbox.delete(0, tk.END)
    existing_domains = dm_functions.fetch_existing_domains()
    for domain in existing_domains:
        existing_domains_listbox.insert(tk.END, domain)

def update_feedback(message):
    feedback_text.config(state=tk.NORMAL)
    feedback_text.insert(tk.END, message + "\n\n")
    feedback_text.config(state=tk.DISABLED)

def display_brave_status():
    brave_installed = dm_functions.check_brave_installation()
    if brave_installed:
        update_feedback("Brave is installed on this system.")
    else:
        update_feedback("Brave is not installed on this system.")

def display_registry_path():
    path_result = dm_functions.check_registry_path()
    update_feedback(path_result)

def set_default_window_size(root, width_percent, height_percent):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    default_width = int(screen_width * width_percent / 100)
    default_height = int(screen_height * height_percent / 100)

    root.geometry(f"{default_width}x{default_height}")

def search_domains(event=None):
    search_text = search_entry.get().strip().lower()
    existing_domains_listbox.delete(0, tk.END)
    if search_text:
        existing_domains = dm_functions.fetch_existing_domains()
        for domain in existing_domains:
            if search_text in domain.lower():
                existing_domains_listbox.insert(tk.END, domain)
    else:
        refresh_existing_domains()

root = tk.Tk()
root.title("Brave Domain Manager")

# Define the icon file path
icon_path = 'icon/Brave_domain_blocker.ico'

# Set the icon for the window
if icon_path:
    # Load the icon using Pillow
    icon = Image.open(icon_path)
    # Convert the image to a format suitable for tkinter
    tk_icon = ImageTk.PhotoImage(icon)
    # Set the window icon
    root.iconphoto(True, tk_icon)

input_frame = tk.Frame(root)
input_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
output_frame = tk.Frame(root)
output_frame.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)

add_label = tk.Label(input_frame, text="Add Domain:")
add_label.pack(anchor=tk.W)
add_entry = tk.Entry(input_frame, width=30)
add_entry.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)
add_entry.bind("<Return>", on_add_button_click)
add_button = tk.Button(input_frame, text="Add", command=on_add_button_click)
add_button.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

search_label = tk.Label(output_frame, text="Search Domain:")
search_label.pack(anchor=tk.W)
search_entry = tk.Entry(output_frame, width=30)
search_entry.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)
search_entry.bind("<KeyRelease>", search_domains)

existing_domains_label = tk.Label(output_frame, text="Existing Domains:")
existing_domains_label.pack(anchor=tk.W)

existing_domains_frame = tk.Frame(output_frame)
existing_domains_frame.pack(expand=True, fill=tk.BOTH)

existing_domains_listbox = tk.Listbox(existing_domains_frame, width=40, height=10, selectmode=tk.SINGLE)
existing_domains_listbox.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(existing_domains_frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

existing_domains_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=existing_domains_listbox.yview)

remove_button = tk.Button(output_frame, text="Remove", command=on_remove_button_click)
remove_button.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

refresh_button = tk.Button(output_frame, text="Refresh", command=on_refresh_button_click)
refresh_button.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

feedback_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
feedback_text.pack(side=tk.BOTTOM, padx=10, pady=10, fill=tk.BOTH, expand=True)
feedback_text.config(state=tk.DISABLED)

# Display Brave installation status
display_brave_status()

# Display registry path check result
display_registry_path()

# Refresh existing domains
refresh_existing_domains()

# Set default window size as a percentage of screen size
set_default_window_size(root, 46, 46)

root.mainloop()
