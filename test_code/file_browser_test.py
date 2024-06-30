import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QFileDialog

class FilePathWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        self.path_field = QLineEdit()
        self.path_field.setPlaceholderText("Enter file path or click Browse...")
        layout.addWidget(self.path_field)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browseFile)
        layout.addWidget(browse_button)

        self.setLayout(layout)

    def browseFile(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select File")
        if file_path:
            self.path_field.setText(file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("File Path Widget")
    layout = QVBoxLayout()
    file_path_widget = FilePathWidget()
    layout.addWidget(file_path_widget)
    window.setLayout(layout)
    window.show()
    sys.exit(app.exec_())
