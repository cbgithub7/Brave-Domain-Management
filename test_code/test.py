import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QListWidget, QTextBrowser

class DocumentationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        # Side column on the left side
        side_column_layout = QVBoxLayout()

        # List widget to display documentation categories or topics
        self.list_widget = QListWidget()
        self.list_widget.addItem("Category 1")
        self.list_widget.addItem("Category 2")
        self.list_widget.addItem("Category 3")
        self.list_widget.itemClicked.connect(self.displayDocumentation)
        side_column_layout.addWidget(self.list_widget)

        layout.addLayout(side_column_layout)

        # QTextBrowser to display documentation
        self.documentation_browser = QTextBrowser()
        layout.addWidget(self.documentation_browser)

        self.setLayout(layout)

    def displayDocumentation(self, item):
        # Dummy function to simulate displaying documentation based on selected item
        selected_item = item.text()
        documentation = f"Documentation for {selected_item}"
        self.documentation_browser.setPlainText(documentation)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Adding documentation tab
        self.documentation_widget = DocumentationWidget()
        self.tabs.addTab(self.documentation_widget, "Documentation")

        self.setLayout(layout)
        self.setWindowTitle("Application Documentation")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec_())
