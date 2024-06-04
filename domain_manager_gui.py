# domain_manager_gui.py
import sys, os
import configparser
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QFileDialog, QSizePolicy, \
    QDesktopWidget, QAbstractItemView, QTabWidget, QMessageBox, QCheckBox, QDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, QEventLoop, QEvent, QUrl, QTimer, QProcess
from PyQt5.QtWebEngineWidgets import QWebEngineView
from qtwidgets import AnimatedToggle
from fuzzywuzzy import fuzz
import qdarktheme
import domain_manager_functions as dm_functions
from custom_prompt import CustomPrompt

# Constants for configuration
APP_ICON_PATH = "icons/Brave_domain_blocker.ico"
ICON_PATH = "icons/question-circle.svg"
DOC_URL = "https://cbgithub7.github.io/Brave-Domain-Manager/"
CONFIG_FILE = 'config.ini'
FILE_FORMATS = [
    ("Text Files", "*.txt"),
    ("CSV Files", "*.csv"),
    ("JSON Files", "*.json"),
    ("All Files", "*.*")
]
SEARCH_THRESHOLD = 70

# Configure logging
logging.basicConfig(filename='domain_manager_gui.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info('Session started')

class DomainManagerGUI(QMainWindow):
    max_button_width = 0

    def __init__(self):
        super().__init__()

        self.cached_domains = []
        self.file_cached_domains = []
        self.current_list = 'existing'
        self.theme = False
        self.show_theme_prompt = True
        self.is_initializing = True

        self.add_entry = QLineEdit()
        self.filepath_entry = QLineEdit()

        self.button_texts = [
            "Submit", "Browse", "Open", "Add to Registry", 
            "Remove from Registry", "Clear List", "Delete Selected", "Refresh List"
        ]
        self.max_button_width = self.calculate_max_button_width(self.button_texts)

        self.initialize_ui()

    def closeEvent(self, event):
        logging.info('Session ended')
        super().closeEvent(event)

    def initialize_ui(self):
        self.setup_window()
        self.setup_layout()
        self.load_preferences()
        self.apply_theme()
        self.display_brave_status()
        self.display_registry_path()
        self.refresh_existing_domains()
        QTimer.singleShot(0, self.check_logging_prompt) 
        self.is_initializing = False

    def check_logging_prompt(self):
        if self.show_logging_prompt:
            self.prompt_for_logging()

    def setup_window(self):
        self.setWindowTitle("Brave Domain Manager")
        self.setWindowIcon(QIcon(APP_ICON_PATH))

        screen = QDesktopWidget().screenGeometry()
        window_width, window_height = int(screen.width() * 0.62), int(screen.height() * 0.60)
        self.resize(QSize(window_width, window_height))

    def setup_layout(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.setup_tabs()
        self.add_lower_frame()

    def setup_tabs(self):
        self.setup_main_tab()
        self.setup_log_tab()
        self.setup_doc_tab()

    def setup_main_tab(self):
        self.domain_tab = QWidget()
        layout = QVBoxLayout(self.domain_tab)

        self.upper_frame = QWidget()
        self.upper_layout = QHBoxLayout(self.upper_frame)

        self.left_frame = self.create_left_frame()
        self.right_frame = self.create_right_frame()

        # Set the width ratios for the left and right frames
        self.left_frame.setMaximumWidth(int(self.width() * 0.25))
        self.right_frame.setMaximumWidth(int(self.width() * 0.75))

        self.upper_layout.addWidget(self.left_frame)
        self.upper_layout.addWidget(self.right_frame)
        layout.addWidget(self.upper_frame)

        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)
        layout.addWidget(self.feedback_text)

        self.tab_widget.addTab(self.domain_tab, "Domain Management")

    def create_left_frame(self):
        left_frame = QWidget()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setAlignment(Qt.AlignTop)
        left_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.add_widgets_to_left_frame(left_layout)
        return left_frame

    def add_widgets_to_left_frame(self, layout):
        self.add_label_and_entry(layout, "Add Domain:", self.on_submit_button_click)
        self.add_label_and_entry(layout, "Add from File:", self.on_open_button_click, browse=True)

        self.file_format_text = QLabel(
            "Supported File Formats:\nText File (.txt): One domain per line.\nCSV File (.csv): One domain per row.\nJSON File (.json): Array of domain strings."
        )
        layout.addWidget(self.file_format_text)

    def add_label_and_entry(self, layout, label_text, submit_callback, browse=False):
        layout.addWidget(QLabel(label_text))
        entry = QLineEdit()
        entry.setPlaceholderText("Enter a domain manually" if not browse else "Enter file path or browse to select")
        entry.returnPressed.connect(submit_callback)
        layout.addWidget(entry)

        if not browse:
            self.add_entry = entry  # Keep reference to the add_entry field
            button_layout = QHBoxLayout()
            button_layout.addWidget(self.create_button("Submit", submit_callback), alignment=Qt.AlignCenter)
            layout.addLayout(button_layout)
        else:
            self.filepath_entry = entry  # Keep reference to the filepath_entry field
            button_layout = QHBoxLayout()
            button_layout.addWidget(self.create_button("Browse", self.on_file_browse_button_click), alignment=Qt.AlignCenter)
            button_layout.addWidget(self.create_button("Open", submit_callback), alignment=Qt.AlignCenter)
            layout.addLayout(button_layout)

    def create_right_frame(self):
        right_frame = QWidget()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignTop)
        right_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.search_label = QLabel("Search Domains: (Click either list to search)   Use Enter shortcut to perform a search.")
        right_layout.addWidget(self.search_label)

        self.search_entry = QLineEdit()
        self.search_entry.textChanged.connect(self.search_domains)
        self.search_entry.returnPressed.connect(self.search_domains)
        right_layout.addWidget(self.search_entry)

        self.add_domain_lists(right_layout)
        return right_frame

    def add_domain_lists(self, layout):
        lists_layout = QHBoxLayout()  # Create a horizontal layout for the lists

        # File domains list and its buttons
        file_domains_layout = QVBoxLayout()
        self.file_domains_list = self.create_domain_list("Domains from File:")
        file_domains_layout.addWidget(self.file_domains_list)
        
        file_buttons_layout = QHBoxLayout()
        file_buttons_layout.addWidget(self.create_button("Add to Registry", lambda: self.process_domains_from_list("Add")))
        file_buttons_layout.addWidget(self.create_button("Remove from Registry", lambda: self.process_domains_from_list("Remove")))
        file_buttons_layout.addWidget(self.create_button("Clear List", self.on_clear_button_click))
        file_domains_layout.addLayout(file_buttons_layout)
        
        lists_layout.addLayout(file_domains_layout)

        # Existing domains list and its buttons
        existing_domains_layout = QVBoxLayout()
        self.existing_domains_list = self.create_domain_list("Blocked Domains:")
        existing_domains_layout.addWidget(self.existing_domains_list)
        
        existing_buttons_layout = QHBoxLayout()
        existing_buttons_layout.addWidget(self.create_button("Delete Selected", self.on_delete_selected_button_click))
        existing_buttons_layout.addWidget(self.create_button("Refresh List", self.on_refresh_button_click))
        existing_domains_layout.addLayout(existing_buttons_layout)
        
        lists_layout.addLayout(existing_domains_layout)

        layout.addLayout(lists_layout)

    def create_domain_list(self, label_text):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(label_text))
        domain_list = QListWidget()
        domain_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        layout.addWidget(domain_list)
        return domain_list

    def setup_log_tab(self):
        self.log_tab = QWidget()
        layout = QVBoxLayout(self.log_tab)

        self.logging_enabled_checkbox = QCheckBox("Enable Logging")
        self.logging_enabled_checkbox.setChecked(True)
        self.logging_enabled_checkbox.stateChanged.connect(self.toggle_logging)
        layout.addWidget(self.logging_enabled_checkbox)

        self.log_options = {
            "Startup/Shutdown Logs": QCheckBox("Startup/Shutdown Logs"),
            "Registry Access Logs": QCheckBox("Registry Access Logs"),
            "Success/Error Logs": QCheckBox("Success/Error Logs"),
            "User Activity Logs": QCheckBox("User Activity Logs"),
            "Configuration Changes": QCheckBox("Configuration Changes"),
            "Audit Logs": QCheckBox("Audit Logs"),
            "Performance Logs": QCheckBox("Performance Logs"),
            "Security Logs": QCheckBox("Security Logs")
        }

        for key, checkbox in self.log_options.items():
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(lambda state, key=key: self.change_log_type(state, key))
            layout.addWidget(checkbox)

        self.tab_widget.addTab(self.log_tab, "Settings")
        self.toggle_logging(self.logging_enabled_checkbox.isChecked())  # Set initial state based on checkbox

    def toggle_logging(self, state):
        enable = state == Qt.Checked
        for checkbox in self.log_options.values():
            checkbox.setEnabled(enable)

        if enable:
            logging.disable(logging.NOTSET)
            logging.info('Logging enabled')
        else:
            logging.disable(logging.CRITICAL)
            logging.info('Logging disabled')

    def change_log_type(self, state, key):
        log_types = {
            "Startup/Shutdown Logs": logging.INFO,
            "Registry Access Logs": logging.INFO,
            "Success/Error Logs": logging.INFO,
            "User Activity Logs": logging.INFO,
            "Configuration Changes": logging.INFO,
            "Audit Logs": logging.WARNING,
            "Performance Logs": logging.INFO,
            "Security Logs": logging.WARNING
        }

        if state == Qt.Checked:
            logging.getLogger(key).setLevel(log_types[key])
            logging.info(f'{key} logging enabled')
        else:
            logging.getLogger(key).setLevel(logging.CRITICAL + 1)
            logging.info(f'{key} logging disabled')

    def setup_doc_tab(self):
        self.doc_tab = QWidget()
        layout = QVBoxLayout(self.doc_tab)
        self.webview = QWebEngineView()
        self.webview.load(QUrl(DOC_URL))
        layout.addWidget(self.webview)
        self.tab_widget.addTab(self.doc_tab, "Documentation")

    def add_lower_frame(self):
        lower_frame = QWidget()
        lower_layout = QHBoxLayout(lower_frame)
        lower_layout.setContentsMargins(0, 0, 0, 0)
        lower_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.current_domain_label = QLabel("Brave Domain Manager is ready. Add or remove domains to block.")
        lower_layout.addWidget(self.current_domain_label)

        self.theme_toggle_switch = AnimatedToggle(checked_color="#FFB000", pulse_checked_color="#00000000", pulse_unchecked_color="#00000000")
        self.theme_toggle_switch.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.theme_toggle_switch.setFixedSize(int(45 * self.logicalDpiX() / 96), int(32 * self.logicalDpiY() / 96))
        self.theme_toggle_switch.toggled.connect(self.on_theme_toggle)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lower_layout.addWidget(spacer)
        lower_layout.addWidget(self.theme_toggle_switch)

        self.main_layout.addWidget(lower_frame)

    def save_preference(self, section, key, value):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        
        print(f"section: {section}, key: {key}, value: {value}")

        if not config.has_section(section):
            config.add_section(section)
        
        config[section][key] = str(value)
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

    def apply_theme(self):
        theme = "dark" if self.theme else "light"
        qdarktheme.setup_theme(theme)
        placeholder_color = "#CCCCCC" if self.theme else "#666666"
        text_color = "white" if self.theme else "black"
        self.add_entry.setStyleSheet(f"QLineEdit {{ color: {text_color}; }} QLineEdit::placeholder {{ color: {placeholder_color}; }} QLineEdit:focus {{ color: {text_color}; }}")
        self.filepath_entry.setStyleSheet(f"QLineEdit {{ color: {text_color}; }} QLineEdit::placeholder {{ color: {placeholder_color}; }} QLineEdit:focus {{ color: {text_color}; }}")

    def create_default_config(self):
        config = configparser.ConfigParser()
        config['Theme'] = {
            'theme': 'False',
            'show_theme_prompt': 'True'
        }
        config['Logging'] = {
            'logging': 'False',
            'show_logging_prompt': 'True'
        }
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

    def prompt_for_logging(self):
        prompt = CustomPrompt(
            title = 'Enable Logging',
            message = 'Enabling logging will restart the application.',
            icon_path = ICON_PATH
        )
        result = prompt.exec_()
        dont_show_again = prompt.get_checkbox_state()

        if dont_show_again:
            self.save_preference('Logging', 'show_logging_prompt', False)

        if result == QDialog.Accepted:
            self.save_preference('Logging', 'logging', True)
            self.logging_enabled_checkbox.setChecked(True)
            self.restart_application()
        else:
            self.save_preference('Logging', 'logging', self.logging_enabled_checkbox.isChecked())
            self.logging_enabled_checkbox.setChecked(False)

    def restart_application(self):
        QApplication.exit()
        QProcess.startDetached(sys.executable, sys.argv)

    def on_theme_toggle(self, state):
        if self.is_initializing:
            return

        self.theme = state
        self.apply_theme()

        if self.show_theme_prompt:
            prompt = CustomPrompt(
                title = 'Set Default Theme',
                message = f'Would you like to make the {"dark" if self.theme else "light"} theme your default theme?',
                icon_path = ICON_PATH
            )
            result = prompt.exec_()
            dont_show_again = prompt.get_checkbox_state()

            if dont_show_again:
                self.save_preference('Theme', 'show_theme_prompt', False)
                self.show_theme_prompt = False

            if prompt.user_closed or result == QDialog.rejected:
                self.theme_toggle_switch.setChecked(not self.theme)
                self.theme = not self.theme
                self.apply_theme()
            elif result == QDialog.Accepted:
                self.save_preference('Theme', 'theme', self.theme)

    def load_preferences(self):
        config = configparser.ConfigParser()
        if not os.path.exists(CONFIG_FILE):
            self.create_default_config()
        config.read(CONFIG_FILE)
        
        if not config.has_section('Theme'):
            config.add_section('Theme')
        self.theme = config.getboolean('Theme', 'theme', fallback=False)
        self.show_theme_prompt = config.getboolean('Theme', 'show_theme_prompt', fallback=True)
        self.theme_toggle_switch.setChecked(self.theme)
        
        if not config.has_section('Logging'):
            config.add_section('Logging')
        self.show_logging_prompt = config.getboolean('Logging', 'show_logging_prompt', fallback=True)
        self.logging_enabled_checkbox.setChecked(config.getboolean('Logging', 'enabled', fallback=False))

    def calculate_max_button_width(self, button_texts):
        padding = 20
        return max(QPushButton(text).fontMetrics().boundingRect(text).width() + padding for text in button_texts)

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setFixedWidth(self.max_button_width)
        return button

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
            if source in (self.file_domains_list, self.existing_domains_list):
                self.search_domains()
                return True
        return super().eventFilter(source, event)

    def on_submit_button_click(self):
        domain = self.add_entry.text()
        if not domain:
            self.update_feedback("Please enter a domain.")
            return

        try:
            cleaned_domain = dm_functions.clean_domain(domain)
            result = dm_functions.add_domain(cleaned_domain)
            self.update_feedback(result)
            self.refresh_existing_domains()
            self.update_current_domain(cleaned_domain, "Add", single_domain=True)

            self.highlight_domains_in_list([cleaned_domain])
            self.add_entry.clear()
            self.add_entry.setFocus()
        except ValueError as e:
            self.update_feedback(f"Invalid domain format: {e}")

    def highlight_domains_in_list(self, domains):
        for domain in domains:
            items = self.existing_domains_list.findItems(domain, Qt.MatchExactly)
            if items:
                item = items[0]
                item.setSelected(True)
                self.existing_domains_list.scrollToItem(item, QAbstractItemView.PositionAtTop)

    def on_delete_selected_button_click(self):
        selected_items = self.existing_domains_list.selectedItems()
        if not selected_items:
            self.update_feedback("No domains selected for deletion.")
            return

        single_domain = len(selected_items) == 1
        for item in selected_items:
            domain = item.text()
            result = dm_functions.remove_domain(domain)
            self.update_feedback(result)
            self.update_current_domain(domain, "Remove", single_domain=single_domain)
            QEventLoop().processEvents()

        self.refresh_existing_domains()
        self.update_current_domain(domain, "Remove", final_message=True, single_domain=single_domain)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.on_delete_key_press()

    def on_delete_key_press(self):
        if self.existing_domains_list.hasFocus():
            selected_items = self.existing_domains_list.selectedItems()
            if selected_items:
                self.on_delete_selected_button_click()

    def on_clear_button_click(self):
        if not self.file_domains_list.count():
            self.update_feedback("The list is already empty.")
            return

        self.file_domains_list.clear()
        self.file_cached_domains.clear()
        self.update_feedback("The list has been cleared.")

    def on_refresh_button_click(self):
        self.refresh_existing_domains()
        self.update_feedback("List refreshed.")

    def on_file_browse_button_click(self):
        filters = ";;".join([f"{name} ({ext})" for name, ext in FILE_FORMATS])
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", filters, initialFilter="All Files (*.*)")
        if file_path:
            self.filepath_entry.setText(file_path)

    def on_open_button_click(self):
        file_path = self.filepath_entry.text()
        if not file_path:
            self.update_feedback("Please enter a file path or use the Browse button to select a file.")
            return

        file_name = os.path.basename(file_path)
        self.populate_file_domains_list(file_path, file_name)

    def populate_file_domains_list(self, file_path, file_name):
        if not file_path:
            self.update_feedback("Please provide a file path.")
            return

        processing_function = self.get_processing_function(file_path)
        if not processing_function:
            self.update_feedback("Unsupported file format. Please use .txt, .csv, or .json.")
            return

        self.file_domains_list.clear()
        self.file_cached_domains.clear()

        domains = []
        try:
            for _, domain in processing_function(file_path):
                try:
                    cleaned_domain = dm_functions.clean_domain(domain)
                    self.file_domains_list.addItem(cleaned_domain)
                    domains.append(cleaned_domain)
                except ValueError as e:
                    self.update_feedback(f"Skipping invalid domain: {e}")

            self.file_cached_domains.append((file_name, domains))
            self.update_feedback(f"Loaded domains from {file_path}")
        except Exception as e:
            self.update_feedback(str(e))

    def get_processing_function(self, file_path):
        if file_path.endswith(".txt"):
            return dm_functions.process_text_file
        elif file_path.endswith(".csv"):
            return dm_functions.process_csv_file
        elif file_path.endswith(".json"):
            return dm_functions.process_json_file
        return None

    def process_domains_from_list(self, action_type):
        selected_items = self.file_domains_list.selectedItems()

        if not self.file_cached_domains:
            self.update_feedback(f"No domains to {action_type.lower()}.")
            return

        file_name = self.file_cached_domains[0][0]
        domains, message = self.get_domains_and_message(selected_items, file_name, action_type)

        reply = QMessageBox.question(self, 'Confirmation', message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            added_domains = []  # To keep track of added domains
            for domain in domains:
                result = self.perform_domain_action(domain, action_type)
                self.update_feedback(result)
                self.update_current_domain(domain, action_type, file_name=file_name)
                if action_type == "Add":
                    added_domains.append(domain)
                QEventLoop().processEvents()

            self.refresh_existing_domains()
            self.update_current_domain("", action_type, final_message=True, file_name=file_name)
            
            # Highlight added domains in the existing domains list
            if action_type == "Add":
                self.highlight_domains_in_list(added_domains)

    def get_domains_and_message(self, selected_items, file_name, action_type):
        if selected_items:
            domains = [item.text() for item in selected_items]
            message = f"Do you want to {action_type.lower()} the selected domains?"
        else:
            domains = self.file_cached_domains[0][1]
            message = f"Do you want to {action_type.lower()} all domains from {file_name}?"
        return domains, message

    def perform_domain_action(self, domain, action_type):
        if action_type == "Add":
            return dm_functions.add_domain(domain)
        elif action_type == "Remove":
            return dm_functions.remove_domain(domain)
        return f"Unsupported action type: {action_type}"

    def update_current_domain(self, domain, action_type, final_message=False, single_domain=False, file_name=None):
        if len(domain) > 100:
            domain = domain[:97] + "..."

        message = self.create_action_message(domain, action_type, file_name)
        self.current_domain_label.setText(message)

        if final_message:
            success_message = self.create_success_message(domain, action_type, single_domain, file_name)
            self.current_domain_label.setText(success_message)

    def create_action_message(self, domain, action_type, file_name):
        if action_type == "Add":
            return f"Adding {domain} from {file_name} to the block list." if file_name else f"Adding {domain} to the block list."
        elif action_type == "Remove":
            return f"Removing {domain} from {file_name} from the block list." if file_name else f"Removing {domain} from the block list."
        return f"{action_type} {domain}"

    def create_success_message(self, domain, action_type, single_domain, file_name):
        if action_type == "Add":
            return f"The domain {domain} has been successfully added to the block list." if single_domain else f"All domains from {file_name} have been successfully added to the block list."
        elif action_type == "Remove":
            return f"The domain {domain} has been successfully removed from the block list." if single_domain else f"All domains from {file_name} have been successfully removed from the block list."
        return "Operation completed successfully."

    def update_feedback(self, message):
        self.feedback_text.append(message)
        self.feedback_text.verticalScrollBar().setValue(self.feedback_text.verticalScrollBar().maximum())
        logging.info(message)

    def display_brave_status(self):
        result = dm_functions.check_brave_installation()
        self.update_feedback("Brave is installed on this system." if result else "Brave is not installed on this system.")

    def display_registry_path(self):
        path_result = dm_functions.check_registry_path()
        self.update_feedback(path_result)

    def refresh_existing_domains(self):
        self.existing_domains_list.clear()
        self.cached_domains = dm_functions.fetch_existing_domains()
        if isinstance(self.cached_domains, list):
            self.existing_domains_list.addItems(self.cached_domains)
        else:
            self.update_feedback(self.cached_domains)

    def search_domains(self):
        search_text = self.search_entry.text()
        domain_list_widget, cached_domains = self.get_current_list_and_cache()
        self.perform_search(search_text, domain_list_widget, cached_domains)

    def get_current_list_and_cache(self):
        if self.current_list == 'existing':
            return self.existing_domains_list, self.cached_domains
        elif self.current_list == 'file':
            return self.file_domains_list, [domain for _, domain_list in self.file_cached_domains for domain in domain_list]
        return None, None

    def perform_search(self, search_text, domain_list_widget, cached_domains):
        domain_list_widget.clear()
        if not search_text:
            domain_list_widget.addItems(cached_domains) if isinstance(cached_domains, list) else self.update_feedback(cached_domains)
            return

        if isinstance(cached_domains, list):
            for domain in cached_domains:
                if fuzz.partial_ratio(search_text.lower(), domain.lower()) >= SEARCH_THRESHOLD:
                    domain_list_widget.addItem(domain)
        else:
            self.update_feedback(cached_domains)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    gui = DomainManagerGUI()
    gui.show()
    logging.info('Application started')
    sys.exit(app.exec_())
