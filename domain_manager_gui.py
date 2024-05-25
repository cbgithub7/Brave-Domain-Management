import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QFileDialog, QSizePolicy, \
    QDesktopWidget, QAbstractItemView, QTabWidget, QTextBrowser, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, QEventLoop, QEvent, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from qtwidgets import AnimatedToggle
from fuzzywuzzy import fuzz
import qdarktheme
import domain_manager_functions as dm_functions

class DomainManagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.cached_domains = []
        self.file_cached_domains = []
        self.current_list = 'existing'

        self.setWindowTitle("Brave Domain Manager")
        self.setWindowIcon(QIcon("icon/Brave_domain_blocker.ico"))
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        # Calculate window size based on screen size
        screen = QDesktopWidget().screenGeometry()
        window_width = int(screen.width() * 0.60)
        window_height = int(screen.height() * 0.60)
        self.resize(QSize(window_width, window_height))

        # Create a tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # Create and add tabs
        self.domain_tab = QWidget()
        self.log_tab = QWidget()
        self.doc_tab = QWidget()
        self.tab_widget.addTab(self.domain_tab, "Domain Management")
        self.tab_widget.addTab(self.log_tab, "Log Viewer")
        self.tab_widget.addTab(self.doc_tab, "Documentation")

        # Add the lower frame
        self.add_lower_frame()

        # Setup tabs
        self.setup_main_tab(window_width)
        self.setup_log_tab()
        self.setup_doc_tab()

        # Set initial state based on saved preference or default
        self.dark_theme_enabled = False  # Set default to dark theme
        self.load_theme_preference()

        # Apply the theme after all necessary widgets are initialized
        self.apply_theme()

        # Populate GUI with initial data
        self.display_brave_status()
        self.display_registry_path()
        self.refresh_existing_domains()

    def setup_main_tab(self, window_width):
        layout = QVBoxLayout()
        self.domain_tab.setLayout(layout)

        # Upper Frame
        self.upper_frame = QWidget()
        self.upper_layout = QHBoxLayout(self.upper_frame)

        # Left Frame
        self.left_frame = QWidget()
        self.left_layout = QVBoxLayout(self.left_frame)
        self.left_layout.setAlignment(Qt.AlignTop)  # Align at the top
        self.left_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.left_frame.setMinimumWidth(int(window_width * 1/4))
        self.left_frame.setMaximumWidth(int(window_width * 1/4))

        self.add_label = QLabel("Add Domain: (Click Submit or press Enter)")
        self.left_layout.addWidget(self.add_label)

        self.add_entry = QLineEdit()
        self.add_entry.setPlaceholderText("Enter a domain manually")
        self.add_entry.returnPressed.connect(self.on_submit_button_click)
        self.left_layout.addWidget(self.add_entry)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.on_submit_button_click)
        self.left_layout.addWidget(self.submit_button)

        self.add_from_file_label = QLabel("Add from File:")
        self.left_layout.addWidget(self.add_from_file_label)

        # Add a filepath input widget
        self.filepath_entry = QLineEdit()
        self.filepath_entry.setPlaceholderText("Enter file path or browse to select")
        self.left_layout.addWidget(self.filepath_entry)

        # Modify the existing browse button and add the new open button
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.on_file_browse_button_click)
        self.left_layout.addWidget(self.browse_button)

        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.on_open_button_click)
        self.left_layout.addWidget(self.open_button)

        self.file_format_text = QLabel(
            "Supported File Formats:\nText File (.txt): One domain per line.\nCSV File (.csv): One domain per row.\nJSON File (.json): Array of domain strings."
        )
        self.left_layout.addWidget(self.file_format_text)

        self.upper_layout.addWidget(self.left_frame)

        # Right Frame
        self.right_frame = QWidget()
        self.right_layout = QVBoxLayout(self.right_frame)
        self.right_layout.setAlignment(Qt.AlignTop)  # Align at the top
        self.right_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.right_frame.setMinimumWidth(int(window_width * 3/4))
        self.right_frame.setMaximumWidth(int(window_width * 3/4))

        self.search_label = QLabel("Search Domains: (Click either list to search)   Use Enter shortcut to perform a search.")
        self.right_layout.addWidget(self.search_label)

        self.search_entry = QLineEdit()
        self.search_entry.textChanged.connect(self.search_domains)  # Dynamic search
        self.search_entry.returnPressed.connect(self.search_domains)  # Search on Enter
        self.right_layout.addWidget(self.search_entry)

        # File domains list
        self.file_domains_label = QLabel("Domains from File:")
        self.file_domains_list = QListWidget()
        self.file_domains_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_domains_list.itemSelectionChanged.connect(self.set_current_list_file)
        self.file_domains_list.installEventFilter(self)  # Install event filter

        # Existing domains list
        self.existing_domains_label = QLabel("Blocked Domains:")
        self.existing_domains_list = QListWidget()
        self.existing_domains_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.existing_domains_list.itemSelectionChanged.connect(self.set_current_list_existing)
        self.existing_domains_list.installEventFilter(self)  # Install event filter

        # Create buttons
        self.add_button = self.create_button("Add to Registry", lambda: self.process_domains_from_list("Add"))
        self.remove_button = self.create_button("Remove from Registry", lambda: self.process_domains_from_list("Remove"))
        self.clear_button = self.create_button("Clear List", self.on_clear_button_click)
        self.delete_button = self.create_button("Delete Selected", self.on_delete_selected_button_click)
        self.refresh_button = self.create_button("Refresh List", self.on_refresh_button_click)

        # List of buttons
        buttons = [self.add_button, self.remove_button, self.clear_button, self.delete_button, self.refresh_button]

        # Calculate the standard width
        max_width = max(button.fontMetrics().boundingRect(button.text()).width() for button in buttons)
        standard_width = max_width + 20  # Add padding (e.g., 20 pixels)

        # Set the standard width for each button
        for button in buttons:
            button.setFixedWidth(standard_width)
        
        # Add button frames
        self.left_button_frame = QWidget()
        self.left_button_layout = QHBoxLayout(self.left_button_frame)

        self.right_button_frame = QWidget()
        self.right_button_layout = QHBoxLayout(self.right_button_frame)

        # Add buttons to layout
        self.left_button_layout.addWidget(self.add_button)
        self.left_button_layout.addWidget(self.remove_button)
        self.left_button_layout.addWidget(self.clear_button)

        self.right_button_layout.addWidget(self.delete_button)
        self.right_button_layout.addWidget(self.refresh_button)

        # Create container widget for side by side layout
        side_by_side_container = QWidget()

        # Add file domains list and existing domains list side by side
        side_by_side_layout = QHBoxLayout(side_by_side_container)
        side_by_side_layout.setContentsMargins(0, 0, 0, 0)

        # Left layout for file domains list
        left_side_layout = QVBoxLayout()
        left_side_layout.addWidget(self.file_domains_label)
        left_side_layout.addWidget(self.file_domains_list)
        left_side_layout.addWidget(self.left_button_frame)

        # Right layout for existing domains list
        right_side_layout = QVBoxLayout()
        right_side_layout.addWidget(self.existing_domains_label)
        right_side_layout.addWidget(self.existing_domains_list)
        right_side_layout.addWidget(self.right_button_frame)

        # Add left and right layouts to the side by side layout
        side_by_side_layout.addLayout(left_side_layout)
        side_by_side_layout.addLayout(right_side_layout)

        # Add container widget to the right layout
        self.right_layout.addWidget(side_by_side_container)

        self.upper_layout.addWidget(self.right_frame)

        layout.addWidget(self.upper_frame)

        # Feedback Text
        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)
        layout.addWidget(self.feedback_text)

    def setup_log_tab(self):
        layout = QVBoxLayout()
        self.log_tab.setLayout(layout)

        # Add placeholder file viewer
        placeholder_viewer = QTextBrowser()
        placeholder_viewer.setPlainText("Placeholder File Viewer")
        layout.addWidget(placeholder_viewer)

    def setup_doc_tab(self):
        layout = QVBoxLayout()
        self.doc_tab.setLayout(layout)

        # Create a QWebEngineView instance
        self.webview = QWebEngineView()

        # Convert the URL string to a QUrl object
        url = QUrl("https://cbgithub7.github.io/Brave-Domain-Manager/")

        # Load the specified URL
        self.webview.load(url)

        # Add the QWebEngineView to the layout
        layout.addWidget(self.webview)

    def add_lower_frame(self):
        # Lower Frame
        lower_frame = QWidget()
        lower_layout = QHBoxLayout(lower_frame)
        lower_layout.setContentsMargins(0, 0, 0, 0)
        lower_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Set background color of the lower frame to transparent
        lower_frame.setStyleSheet("background-color: transparent;")

        # Feedback label for displaying the current domain being processed
        self.current_domain_label = QLabel("Brave Domain Manager is ready. Add or remove domains to block.")
        lower_layout.addWidget(self.current_domain_label)

        # Add AnimatedToggle widget for theme switching
        theme_toggle_switch = AnimatedToggle(
            checked_color="#FFB000",
            pulse_checked_color="#00000000",
            pulse_unchecked_color="#00000000"
        )

        # Set the size policy of the toggle switch
        theme_toggle_switch.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Define the size in density-independent pixels for both width and height
        toggle_width_dp = 45
        toggle_height_dp = 32

        # Calculate the size in pixels based on the current screen's pixel density for width
        toggle_width_px = int(toggle_width_dp * self.logicalDpiX() / 96)

        # Calculate the size in pixels based on the current screen's pixel density for height
        toggle_height_px = int(toggle_height_dp * self.logicalDpiY() / 96)

        # Set the fixed size of the toggle switch
        theme_toggle_switch.setFixedSize(toggle_width_px, toggle_height_px)

        # Add spacer to push the toggle switch to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lower_layout.addWidget(spacer)

        # Add the toggle switch to the layout
        lower_layout.addWidget(theme_toggle_switch)
        theme_toggle_switch.toggled.connect(self.toggle_theme)

        self.main_layout.addWidget(lower_frame)

    def toggle_theme(self, state):
        self.dark_theme_enabled = state  # state is True for dark theme, False for light theme
        self.save_theme_preference()
        self.apply_theme()

    def apply_theme(self):
        if self.dark_theme_enabled:
            qdarktheme.setup_theme("dark")
            placeholder_color = "#CCCCCC"
            text_color = "white"  # Lighter color for dark theme
        else:
            qdarktheme.setup_theme("light")
            placeholder_color = "#666666"
            text_color = "black"  # Black color for light theme

        # Set placeholder text color for input fields
        self.add_entry.setStyleSheet("QLineEdit { color: %s; }"
                                    "QLineEdit::placeholder { color: %s; }"
                                    "QLineEdit:focus { color: %s; }" % (text_color, placeholder_color, text_color))
        self.filepath_entry.setStyleSheet("QLineEdit { color: %s; }"
                                    "QLineEdit::placeholder { color: %s; }"
                                    "QLineEdit:focus { color: %s; }" % (text_color, placeholder_color, text_color))

    def save_theme_preference(self):
        # Save the current theme preference (e.g., to a settings file or database)
        pass

    def load_theme_preference(self):
        # Load the saved theme preference (e.g., from a settings file or database)
        pass

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.clicked.connect(callback)
        return button

    #Layout Functionality--------------------------------------------------------------------------------------------------

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
            if source in (self.file_domains_list, self.existing_domains_list):
                self.search_domains()
                return True
        return super().eventFilter(source, event)
    
    def on_submit_button_click(self):
        domain = self.add_entry.text()
        if domain:
            try:
                cleaned_domain = dm_functions.clean_domain(domain)
                result = dm_functions.add_domain(cleaned_domain)
                self.update_feedback(result)
                self.refresh_existing_domains()
                self.update_current_domain(cleaned_domain, action_type="Add", final_message=True, single_domain=True)

                # Highlight the newly added domain
                items = self.existing_domains_list.findItems(cleaned_domain, Qt.MatchExactly)
                if items:
                    item = items[0]
                    item.setSelected(True)
                    self.existing_domains_list.scrollToItem(item, QAbstractItemView.PositionAtTop)

                self.add_entry.clear()
                self.add_entry.setFocus()
            except ValueError as e:
                self.update_feedback(f"Invalid domain format: {e}")

    def on_delete_selected_button_click(self):
        selected_items = self.existing_domains_list.selectedItems()
        if selected_items:
            # Check if only one item is selected
            single_domain = len(selected_items) == 1
            for item in selected_items:
                domain = item.text()
                result = dm_functions.remove_domain(domain)
                self.update_feedback(result)
                self.update_current_domain(domain, action_type="Remove", single_domain=single_domain)
                QEventLoop().processEvents()  # Process GUI events to update the display

            # After all domains are removed, refresh the existing domains list
            self.refresh_existing_domains()

            # Display the final success message
            self.update_current_domain(domain, action_type="Remove", final_message=True, single_domain=single_domain)

    def on_delete_key_press(self):
        if self.existing_domains_list.hasFocus():
            selected_items = self.existing_domains_list.selectedItems()
            if selected_items:
                for item in selected_items:
                    self.on_delete_selected_button_click()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.on_delete_key_press()

    def on_clear_button_click(self):
        self.file_domains_list.clear()
        self.file_cached_domains.clear()

    def on_refresh_button_click(self):
        self.refresh_existing_domains()
        self.update_feedback("List refreshed.")

    def on_file_browse_button_click(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "All Files (*);;Text Files (*.txt);;CSV Files (*.csv);;JSON Files (*.json)"
        )
        if file_path:
            self.filepath_entry.setText(file_path)  # Populate the filepath widget with the selected path

    def on_open_button_click(self):
        file_path = self.filepath_entry.text()
        if file_path:
            file_name = os.path.basename(file_path)
            self.populate_file_domains_list(file_path, file_name)

    def populate_file_domains_list(self, file_path, file_name):
        if not file_path:
            self.update_feedback("Please provide a file path.")
            return

        if file_path.endswith(".txt"):
            processing_function = dm_functions.process_text_file
        elif file_path.endswith(".csv"):
            processing_function = dm_functions.process_csv_file
        elif file_path.endswith(".json"):
            processing_function = dm_functions.process_json_file
        else:
            self.update_feedback("Unsupported file format. Please use .txt, .csv, or .json.")
            return

        self.file_domains_list.clear()
        self.file_cached_domains.clear()

        domains = []
        for _, domain in processing_function(file_path, self.update_feedback):  # Adjusted to only unpack domain
            try:
                cleaned_domain = dm_functions.clean_domain(domain)
                self.file_domains_list.addItem((cleaned_domain))
                domains.append(cleaned_domain)
            except ValueError as e:
                self.update_feedback(f"Skipping invalid domain: {e}")

        self.file_cached_domains.append((file_name, domains))
        self.update_feedback(f"Loaded domains from {file_path}")

    def process_domains_from_list(self, action_type):
        selected_items = self.file_domains_list.selectedItems()
        
        if not self.file_cached_domains:
            self.update_feedback(f"No domains to {action_type.lower()}.")
            return
        
        file_name = self.file_cached_domains[0][0]

        if selected_items:
            domains = [item.text() for item in selected_items]
            message = f"Do you want to {action_type.lower()} the selected domains?"
        else:
            if not self.file_cached_domains:
                self.update_feedback(f"No domains to {action_type.lower()}.")
                return
            
            domains = self.file_cached_domains[0][1]
            message = f"Do you want to {action_type.lower()} all domains from {file_name}?"

        reply = QMessageBox.question(self, 'Confirmation', message,
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            for domain in domains:
                if action_type == "Add":
                    result = dm_functions.add_domain(domain)
                elif action_type == "Remove":
                    result = dm_functions.remove_domain(domain)
                else:
                    self.update_feedback(f"Unsupported action type: {action_type}")
                    return

                self.update_feedback(result)
                self.update_current_domain(domain, action_type=action_type, file_name=file_name)
                QEventLoop().processEvents()  # Process GUI events to update the display

            self.refresh_existing_domains()

            # Display the final success message
            self.update_current_domain("", action_type=action_type, final_message=True, file_name=file_name)

    def update_current_domain(self, domain, action_type, final_message=False, single_domain=False, file_name=None):
        if len(domain) > 100:  # Adjust this threshold as needed
            domain = domain[:97] + "..."  # Truncate long domain names

        if action_type == "Add":
            if file_name:
                message = f"Adding {domain} from {file_name} to the block list."
            else:
                message = f"Adding {domain} to the block list."
        elif action_type == "Remove":
            if file_name:
                message = f"Removing {domain} from {file_name} from the block list."
            else:
                message = f"Removing {domain} from the block list."
        else:
            message = f"{action_type} {domain}"

        self.current_domain_label.setText(message)

        if final_message:
            if action_type == "Add":
                if single_domain:
                    success_message = f"The domain {domain} has been successfully added to the block list."
                else:
                    success_message = f"All domains from {file_name} have been successfully added to the block list."
            elif action_type == "Remove":
                if single_domain:
                    success_message = f"The domain {domain} has been successfully removed from the block list."
                else:
                    if file_name:
                        success_message = f"All domains from {file_name} have been successfully removed from the block list."
                    else:
                        success_message = "All selected domains have been successfully removed from the block list."
            else:
                success_message = "Operation completed successfully."

            self.current_domain_label.setText(success_message)

    def update_feedback(self, message):
        # Function to update the feedback text
        current_text = self.feedback_text.toPlainText()
        self.feedback_text.setPlainText(current_text + message + "\n")

        # Scroll to the bottom of the feedback text widget
        self.feedback_text.verticalScrollBar().setValue(self.feedback_text.verticalScrollBar().maximum())

    def display_brave_status(self):
        result = dm_functions.check_brave_installation()
        if result:  # If result is True, Brave is installed
            message = "Brave is installed on this system."
        else:  # If result is False, Brave is not installed
            message = "Brave is not installed on this system."
        self.update_feedback(message)

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

    def set_current_list_existing(self):
        self.reset_list('file')  # Reset the file list to display all domains
        self.current_list = 'existing'
        #self.search_domains()

    def set_current_list_file(self):
        self.reset_list('existing')  # Reset the existing list to display all domains
        self.current_list = 'file'
        #self.search_domains()

    def reset_list(self, list_type):
        if list_type == 'existing':
            domain_list_widget = self.existing_domains_list
            cached_domains = self.cached_domains
        elif list_type == 'file':
            domain_list_widget = self.file_domains_list
            cached_domains = [domain for _, domain_list in self.file_cached_domains for domain in domain_list]
        else:
            return

        domain_list_widget.clear()
        domain_list_widget.addItems(cached_domains)

    def search_domains(self):
        search_text = self.search_entry.text()

        if self.current_list == 'existing':
            domain_list_widget = self.existing_domains_list
            cached_domains = self.cached_domains
        elif self.current_list == 'file':
            domain_list_widget = self.file_domains_list
            cached_domains = [domain for _, domain_list in self.file_cached_domains for domain in domain_list]
        else:
            return

        self.perform_search(search_text, domain_list_widget, cached_domains)

    def perform_search(self, search_text, domain_list_widget, cached_domains):
        domain_list_widget.clear()

        if not search_text:
            if isinstance(cached_domains, list):
                domain_list_widget.addItems(cached_domains)
            else:
                self.update_feedback(cached_domains)
            return

        if isinstance(cached_domains, list):
            for domain in cached_domains:
                similarity_score = fuzz.partial_ratio(search_text.lower(), domain.lower())
                if similarity_score >= 70:  # Adjust threshold as needed
                    domain_list_widget.addItem(domain)
        else:
            self.update_feedback(cached_domains)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    gui = DomainManagerGUI()
    gui.show()
    sys.exit(app.exec_())
