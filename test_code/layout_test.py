import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QFileDialog, QSizePolicy, \
    QDesktopWidget, QAbstractItemView, QTabWidget, QTextBrowser, QMessageBox
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon


class DemoApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tab Layout Demo")
        self.setWindowIcon(QIcon("icon.png"))  # Change "icon.png" to the path of your icon file

        # Calculate window size based on screen size
        screen = QDesktopWidget().screenGeometry()
        window_width = int(screen.width() * 0.60)
        window_height = int(screen.height() * 0.60)
        self.resize(QSize(window_width, window_height))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.setup_tab_layout()

    def setup_tab_layout(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        tab.setLayout(layout)

        # Replace the following line with the setup_main_tab method from your code
        self.setup_main_tab(layout)

        self.tab_widget.addTab(tab, "Main Tab")

    # Replace the below method with your setup_main_tab method
    def setup_main_tab(self, layout, window_width):
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


def main():
    app = QApplication(sys.argv)
    window = DemoApp()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
