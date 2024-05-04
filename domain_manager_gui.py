import tkinter as tk
from tkinter import filedialog, scrolledtext
import domain_manager_functions as dm_functions

def on_add_button_click(event=None):
    domain = add_entry.get()
    if domain:
        result = dm_functions.add_domain(domain)
        update_feedback(result)
        refresh_existing_domains()
        # Scroll to the bottom after adding a domain
        existing_domains_listbox.yview_moveto(1.0)

def on_remove_button_click():
    index = existing_domains_listbox.curselection()
    if index:
        result = dm_functions.remove_domain(existing_domains_listbox.get(index))
        update_feedback(result)
        refresh_existing_domains()

def on_refresh_button_click():
    refresh_existing_domains()
    update_feedback("List refreshed.")

def on_file_browse_button_click():
    file_path = filedialog.askopenfilename(filetypes=[
        ("All Files", "*.*"), 
        ("Text Files", "*.txt"), 
        ("CSV Files", "*.csv"), 
        ("JSON Files", "*.json")
    ])
    if file_path:
        # Process the selected file
        process_file(file_path)

def process_file(file_path):
    if file_path.endswith(".txt"):
        new_domains = dm_functions.process_text_file(file_path, update_feedback)
    elif file_path.endswith(".csv"):
        new_domains = dm_functions.process_csv_file(file_path, update_feedback)
    elif file_path.endswith(".json"):
        new_domains = dm_functions.process_json_file(file_path, update_feedback)
    else:
        update_feedback("Unsupported file format.")
        return

    refresh_existing_domains()

def refresh_existing_domains():
    existing_domains_listbox.delete(0, tk.END)
    existing_domains = dm_functions.fetch_existing_domains()
    for domain in existing_domains:
        existing_domains_listbox.insert(tk.END, domain)

def update_feedback(message):
    feedback_text.config(state=tk.NORMAL)
    feedback_text.insert(tk.END, message + "\n\n")
    feedback_text.see(tk.END)  # Scroll to the end
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

def clear_placeholder(event):
    if add_entry.get() == "Enter a domain manually":
        add_entry.delete(0, tk.END)
        add_entry.config(fg="black")  # Change text color to black when editing

def add_placeholder(event):
    if not add_entry.get():
        add_entry.insert(0, "Enter a domain manually")
        add_entry.config(fg="gray")  # Change text color to gray when not editing

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
    root.iconbitmap(icon_path)

# Create a PanedWindow widget
paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
paned_window.pack(fill=tk.BOTH, expand=True)

# Create left frame for input elements
left_frame = tk.Frame(paned_window)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)  # Set expand to False

# Create right frame for output elements
right_frame = tk.Frame(paned_window)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  # Set expand to True

# Add left and right frames to the PanedWindow
paned_window.add(left_frame)
paned_window.add(right_frame)

add_label = tk.Label(left_frame, text="Add Domain:")
add_label.pack(anchor=tk.W)
add_entry = tk.Entry(left_frame, width=30)
add_entry.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)
add_entry.insert(0, "Enter a domain manually")  # Placeholder text
add_entry.config(fg="gray")  # Set text color to gray
add_entry.bind("<FocusIn>", clear_placeholder)  # Clear placeholder text when focused
add_entry.bind("<FocusOut>", add_placeholder)  # Add placeholder text when focus is lost
add_entry.bind("<Return>", on_add_button_click)

add_button = tk.Button(left_frame, text="Add", command=on_add_button_click)
add_button.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

add_from_file_label = tk.Label(left_frame, text="Add from File:")
add_from_file_label.pack(anchor=tk.W)

browse_button = tk.Button(left_frame, text="Browse", command=on_file_browse_button_click)
browse_button.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)

file_format_text = tk.Label(left_frame, text="Supported File Formats:\nText File (.txt): One domain per line.\nCSV File (.csv): One domain per row.\nJSON File (.json): Array of domain strings.")
file_format_text.pack(anchor=tk.W)

search_label = tk.Label(right_frame, text="Search Domain:")
search_label.pack(anchor=tk.W)
search_entry = tk.Entry(right_frame, width=30)
search_entry.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X)
search_entry.bind("<KeyRelease>", search_domains)

existing_domains_label = tk.Label(right_frame, text="Existing Domains:")
existing_domains_label.pack(anchor=tk.W)

existing_domains_frame = tk.Frame(right_frame)
existing_domains_frame.pack(expand=True, fill=tk.BOTH)

existing_domains_listbox = tk.Listbox(existing_domains_frame, width=40, height=10, selectmode=tk.SINGLE)
existing_domains_listbox.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(existing_domains_frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

existing_domains_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=existing_domains_listbox.yview)

# Create a frame for the remove and refresh buttons
button_frame = tk.Frame(right_frame)
button_frame.pack(anchor=tk.CENTER, padx=5, pady=5)

remove_button = tk.Button(button_frame, text="Remove", command=on_remove_button_click, width=10)
remove_button.pack(side=tk.LEFT, padx=5)

refresh_button = tk.Button(button_frame, text="Refresh", command=on_refresh_button_click, width=10)
refresh_button.pack(side=tk.LEFT, padx=5)

feedback_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
feedback_text.pack(side=tk.BOTTOM, padx=10, pady=10, fill=tk.BOTH, expand=True)

# Display Brave installation status
display_brave_status()

# Display registry path check result
display_registry_path()

# Refresh existing domains
refresh_existing_domains()

# Set default window size as a percentage of screen size
set_default_window_size(root, 46, 46)

root.mainloop()