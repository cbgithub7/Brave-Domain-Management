import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QFileDialog, QAction, QSizePolicy, \
    QDesktopWidget, QToolBar, QAbstractItemView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, QObject, pyqtSlot
from qtwidgets import AnimatedToggle  # Import AnimatedToggle from qtwidgets
import domain_manager_functions as dm_functions
import qdarktheme

class DomainManagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Brave Domain Manager")
        self.setWindowIcon(QIcon("icon/Brave_domain_blocker.ico"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        # Create toolbar
        self.toolbar = QToolBar()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)  # Display text beside icon
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        # Toolbar actions
        self.undo_action = QAction(QIcon("icon/undo_icon.png"), "Undo", self)
        self.undo_action.triggered.connect(dm_functions.undo_action)
        self.toolbar.addAction(self.undo_action)

        self.redo_action = QAction(QIcon("icon/redo_icon.png"), "Redo", self)
        self.redo_action.triggered.connect(dm_functions.redo_action)
        self.toolbar.addAction(self.redo_action)

        # Add AnimatedToggle widget for theme switching
        self.theme_toggle_switch = AnimatedToggle(
            checked_color="#FFB000",
            pulse_checked_color="#44FFB000"
        )
        
        # Add spacer to push the toggle switch to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)

        # Add the toggle switch to the toolbar
        self.toolbar.addWidget(self.theme_toggle_switch)
        self.theme_toggle_switch.toggled.connect(self.toggle_theme)

        # Set initial state based on saved preference or default
        self.dark_theme_enabled = False  # Set default to dark theme
        self.load_theme_preference()

        # Calculate window size based on screen size
        screen = QDesktopWidget().screenGeometry()
        window_width = int(screen.width() * 0.46)
        window_height = int(screen.height() * 0.46)
        self.resize(QSize(window_width, window_height))

        # Upper Frame
        self.upper_frame = QWidget()
        self.upper_layout = QHBoxLayout(self.upper_frame)

        # Left Frame
        self.left_frame = QWidget()
        self.left_layout = QVBoxLayout(self.left_frame)
        self.left_layout.setAlignment(Qt.AlignTop)  # Align at the top
        self.left_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.left_frame.setMinimumWidth(int(window_width * 1/3))
        self.left_frame.setMaximumWidth(int(window_width * 1/3))

        self.add_label = QLabel("Add Domain: (Click Add or press Enter)")
        self.left_layout.addWidget(self.add_label)

        self.add_entry = QLineEdit()
        self.add_entry.setPlaceholderText("Enter a domain manually")
        self.add_entry.returnPressed.connect(self.on_add_button_click)
        self.left_layout.addWidget(self.add_entry)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.on_add_button_click)
        self.left_layout.addWidget(self.add_button)

        self.add_from_file_label = QLabel("Add from File:")
        self.left_layout.addWidget(self.add_from_file_label)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.on_file_browse_button_click)
        self.left_layout.addWidget(self.browse_button)

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
        self.right_frame.setMinimumWidth(int(window_width * 2/3))
        self.right_frame.setMaximumWidth(int(window_width * 2/3))

        self.search_label = QLabel("Search Domains:")
        self.right_layout.addWidget(self.search_label)

        self.search_entry = QLineEdit()
        self.search_entry.textChanged.connect(self.search_domains)  # Dynamic search
        self.right_layout.addWidget(self.search_entry)

        self.existing_domains_label = QLabel("Blocked Domains:")
        self.right_layout.addWidget(self.existing_domains_label)

        self.existing_domains_list = QListWidget()
        self.existing_domains_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.right_layout.addWidget(self.existing_domains_list)

        self.button_frame = QWidget()
        self.button_layout = QHBoxLayout(self.button_frame)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.on_remove_button_click)
        self.button_layout.addWidget(self.remove_button)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.on_refresh_button_click)
        self.button_layout.addWidget(self.refresh_button)

        self.right_layout.addWidget(self.button_frame)

        self.upper_layout.addWidget(self.right_frame)

        self.main_layout.addWidget(self.upper_frame)

        # Feedback Text
        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)
        self.main_layout.addWidget(self.feedback_text)

        # Apply the theme after all necessary widgets are initialized
        self.apply_theme()

        self.display_brave_status()
        self.display_registry_path()
        self.refresh_existing_domains()

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
            
        # Set placeholder text color for add_entry QLineEdit
        self.add_entry.setStyleSheet("QLineEdit { color: %s; }"
                                    "QLineEdit::placeholder { color: %s; }"
                                    "QLineEdit:focus { color: %s; }" % (text_color, placeholder_color, text_color))

    def save_theme_preference(self):
        # Save the current theme preference (e.g., to a settings file or database)
        pass

    def load_theme_preference(self):
        # Load the saved theme preference (e.g., from a settings file or database)
        pass

    def on_add_button_click(self):
        domain = self.add_entry.text()
        if domain:
            result = dm_functions.add_domain(domain)
            self.update_feedback(result)
            self.refresh_existing_domains()
            self.existing_domains_list.scrollToBottom()

            # Clear input field and return to placeholder text
            self.add_entry.clear()
            self.add_entry.setFocus()

    def on_remove_button_click(self):
        selected_items = self.existing_domains_list.selectedItems()
        if selected_items:
            for item in selected_items:
                result = dm_functions.remove_domain(item.text())
                self.update_feedback(result)
            self.refresh_existing_domains()

    def on_delete_key_press(self):
        if self.existing_domains_list.hasFocus():
            selected_items = self.existing_domains_list.selectedItems()
            if selected_items:
                for item in selected_items:
                    self.on_remove_button_click()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.on_delete_key_press()

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
            self.process_file(file_path)

    def process_file(self, file_path):
        file_extension = file_path.split(".")[-1]
        update_feedback = self.update_feedback
        try:
            if file_extension == "txt":
                new_domains = dm_functions.process_text_file(file_path, update_feedback)
            elif file_extension == "csv":
                new_domains = dm_functions.process_csv_file(file_path, update_feedback)
            elif file_extension == "json":
                new_domains = dm_functions.process_json_file(file_path, update_feedback)
            else:
                self.update_feedback("Unsupported file format.")
                return
            
            self.refresh_existing_domains()

            # Update existing domains list with newly added domains highlighted
            for domain in new_domains:
                cleaned_domain = dm_functions.clean_domain(domain)  # Clean the domain
                items = self.existing_domains_list.findItems(cleaned_domain, Qt.MatchExactly)
                if items:
                    for item in items:
                        item.setSelected(True)
                        self.existing_domains_list.scrollToItem(item)
            
        except Exception as e:
            update_feedback(f"Error processing file: {e}")

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
        existing_domains = dm_functions.fetch_existing_domains()
        if isinstance(existing_domains, list):
            self.existing_domains_list.addItems(existing_domains)
        else:
            self.update_feedback(existing_domains)

    def search_domains(self):
        search_text = self.search_entry.text()
        existing_domains = dm_functions.fetch_existing_domains()
        self.existing_domains_list.clear()
        if isinstance(existing_domains, list):
            matching_domains = [domain for domain in existing_domains if search_text.lower() in domain.lower()]
            self.existing_domains_list.addItems(matching_domains)
        else:
            self.update_feedback(existing_domains)

    def update_feedback(self, message):
        self.feedback_text.append(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Apply the complete dark theme to your Qt App.
    qdarktheme.setup_theme()
    gui = DomainManagerGUI()
    gui.show()
    sys.exit(app.exec_())
