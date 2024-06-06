# custom_prompt.py

# PyQt5 imports
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QCheckBox
from PyQt5.QtGui import QIcon

# Constants
APP_ICON_PATH = "icons/Brave_domain_blocker.ico"

class CustomPrompt(QDialog):
    def __init__(self, title, message, notice, icon_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.user_closed = False
        self.init_ui(message, notice, icon_path)

    def init_ui(self, message, notice, icon_path):
        layout = QVBoxLayout()

        # Warning message with icon
        prompt_layout = QHBoxLayout()
        prompt_icon = QLabel()
        prompt_icon.setPixmap(QIcon(icon_path).pixmap(45, 45))
        prompt_message = QLabel(message)
        prompt_notice = QLabel(notice)
        prompt_notice.setStyleSheet("color: blue; font-weight: bold;")
        prompt_layout.addWidget(prompt_icon)
        prompt_layout.addWidget(prompt_message)
        prompt_layout.addWidget(prompt_notice)
        
        # Don't show again checkbox
        self.checkbox = QCheckBox("Don't show me this again")

        # Buttons
        button_layout = QHBoxLayout()
        self.yes_button = QPushButton("Yes")
        self.no_button = QPushButton("No")
        button_layout.addWidget(self.yes_button)
        button_layout.addWidget(self.no_button)

        layout.addLayout(prompt_layout)
        layout.addWidget(self.checkbox)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.yes_button.clicked.connect(self.accept)
        self.no_button.clicked.connect(self.reject)

    def get_checkbox_state(self):
        return self.checkbox.isChecked()
    
    def closeEvent(self, event):
        self.user_closed = True
        super().closeEvent(event)
