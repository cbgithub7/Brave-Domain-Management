import tkinter as tk
from tkinter import filedialog, scrolledtext
from PIL import Image, ImageTk
import domain_manager_functions as dm_functions
import tkinter.font as tkfont

def on_add_button_click(event=None):
    domain = add_entry.get()
    if domain:
        result = dm_functions.add_domain(domain)
        update_feedback(result)
        refresh_existing_domains()
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
    feedback_text.see(tk.END)
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
        add_entry.config(fg="black")

def add_placeholder(event):
    if not add_entry.get():
        add_entry.insert(0, "Enter a domain manually")
        add_entry.config(fg="gray")

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

def underline_on_enter(event):
    original_font = event.widget.cget("font")
    if original_font:
        if "underline" not in original_font:
            font = tkfont.Font(event.widget, event.widget.cget("font"))
            font.configure(underline=True)
            event.widget.configure(font=font)
            event.widget.original_font = original_font

def remove_underline_on_leave(event):
    if hasattr(event.widget, "original_font"):
        event.widget.configure(font=event.widget.original_font)
        del event.widget.original_font

root = tk.Tk()
root.title("Brave Domain Manager")

icon_path = 'icon/Brave_domain_blocker.ico'
if icon_path:
    root.iconbitmap(icon_path)

paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
paned_window.grid(row=0, column=0, sticky="nsew")

left_frame = tk.Frame(paned_window)
left_frame.grid(row=0, column=0, sticky="nsew")

left_frame.grid_rowconfigure(0, weight=0)
left_frame.grid_columnconfigure(0, weight=1)

right_frame = tk.Frame(paned_window)
right_frame.grid(row=0, column=1, sticky="nsew")

right_frame.grid_rowconfigure(0, weight=0)
right_frame.grid_columnconfigure(0, weight=1)

paned_window.add(left_frame)
paned_window.add(right_frame)

undo_icon = Image.open("icon/undo_icon.png").resize((20, 20), Image.LANCZOS)
redo_icon = Image.open("icon/redo_icon.png").resize((20, 20), Image.LANCZOS)

undo_image = ImageTk.PhotoImage(undo_icon)
redo_image = ImageTk.PhotoImage(redo_icon)

undo_redo_frame = tk.Frame(left_frame)
undo_redo_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

undo_button = tk.Button(undo_redo_frame, text="Undo", image=undo_image, compound=tk.LEFT, command=dm_functions.undo_action, bd=2, relief=tk.RAISED)
undo_button.grid(row=0, column=0, padx=(0, 5), pady=0, sticky="ew")

redo_button = tk.Button(undo_redo_frame, text="Redo", image=redo_image, compound=tk.LEFT, command=dm_functions.redo_action, bd=2, relief=tk.RAISED)
redo_button.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="ew")

# Make buttons full frame width
undo_redo_frame.grid_columnconfigure(0, weight=1)
undo_redo_frame.grid_columnconfigure(1, weight=1)

add_label = tk.Label(left_frame, text="Add Domain:")
add_label.grid(row=1, column=0, columnspan=2, sticky="w")

add_entry = tk.Entry(left_frame, width=30)
add_entry.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
add_entry.insert(0, "Enter a domain manually")
add_entry.config(fg="gray")
add_entry.bind("<FocusIn>", clear_placeholder)
add_entry.bind("<FocusOut>", add_placeholder)
add_entry.bind("<Return>", on_add_button_click)

add_button = tk.Button(left_frame, text="Add", command=on_add_button_click)
add_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

add_from_file_label = tk.Label(left_frame, text="Add from File:")
add_from_file_label.grid(row=4, column=0, columnspan=2, sticky="w")

browse_button = tk.Button(left_frame, text="Browse", command=on_file_browse_button_click)
browse_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

file_format_text = tk.Label(left_frame, text="Supported File Formats:\nText File (.txt): One domain per line.\nCSV File (.csv): One domain per row.\nJSON File (.json): Array of domain strings.")
file_format_text.grid(row=6, column=0, columnspan=2, sticky="w")

search_label = tk.Label(right_frame, text="Search Domains:")
search_label.grid(row=0, column=0, sticky="w")

search_entry = tk.Entry(right_frame, width=30)
search_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
search_entry.bind("<KeyRelease>", search_domains)

existing_domains_label = tk.Label(right_frame, text="Blocked Domains:")
existing_domains_label.grid(row=2, column=0, sticky="w")

existing_domains_frame = tk.Frame(right_frame)
existing_domains_frame.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")

existing_domains_listbox = tk.Listbox(existing_domains_frame, width=40, height=10, selectmode=tk.EXTENDED)
existing_domains_listbox.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="nsew")

scrollbar = tk.Scrollbar(existing_domains_frame, orient=tk.VERTICAL)
scrollbar.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="ns")

existing_domains_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=existing_domains_listbox.yview)

button_frame = tk.Frame(right_frame)
button_frame.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

remove_button = tk.Button(button_frame, text="Remove", command=on_remove_button_click, width=10)
remove_button.grid(row=0, column=0, padx=5, sticky="ew")

refresh_button = tk.Button(button_frame, text="Refresh", command=on_refresh_button_click, width=10)
refresh_button.grid(row=0, column=1, padx=5, sticky="ew")

feedback_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
feedback_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

add_button.bind("<Enter>", underline_on_enter)
add_button.bind("<Leave>", remove_underline_on_leave)
remove_button.bind("<Enter>", underline_on_enter)
remove_button.bind("<Leave>", remove_underline_on_leave)
refresh_button.bind("<Enter>", underline_on_enter)
refresh_button.bind("<Leave>", remove_underline_on_leave)
undo_button.bind("<Enter>", underline_on_enter)
undo_button.bind("<Leave>", remove_underline_on_leave)
redo_button.bind("<Enter>", underline_on_enter)
redo_button.bind("<Leave>", remove_underline_on_leave)
browse_button.bind("<Enter>", underline_on_enter)
browse_button.bind("<Leave>", remove_underline_on_leave)

display_brave_status()
display_registry_path()
refresh_existing_domains()

set_default_window_size(root, 46, 46)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()
