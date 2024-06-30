import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTabWidget, QSizePolicy

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Padding Bottom of Tab Example")
        self.setGeometry(100, 100, 800, 600)  # Set the size of the main window

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        # Create a tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # Add tabs with different layouts
        self.add_tab1()
        self.add_tab2()

        # Add the lower frame
        self.add_lower_frame()

    def add_tab1(self):
        # Tab 1
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)

        # Content widgets
        label1 = QLabel("Content for Tab 1")
        label2 = QLabel("Content for Tab 1")
        tab1_layout.addWidget(label1)
        tab1_layout.addWidget(label2)

        # Add padding at the bottom
        tab1_layout.addSpacing(20)  # Adjust the spacing as needed for padding

        # Add tab1 to the tab widget
        self.tab_widget.addTab(tab1, "Tab 1")

    def add_tab2(self):
        # Tab 2
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)

        # Content widgets
        label1 = QLabel("Content for Tab 2")
        label2 = QLabel("Content for Tab 2")
        tab2_layout.addWidget(label1)
        tab2_layout.addWidget(label2)

        # Add tab2 to the tab widget
        self.tab_widget.addTab(tab2, "Tab 2")

    def add_lower_frame(self):
        # Lower Frame
        lower_frame = QWidget()
        lower_layout = QHBoxLayout(lower_frame)
        lower_layout.setContentsMargins(0, 0, 0, 0)
        lower_layout.setSpacing(0)
        lower_frame.setStyleSheet("background-color: red;")
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lower_frame.setSizePolicy(size_policy)

        # Feedback label for displaying the current domain being processed
        current_domain_label = QLabel("Brave Domain Manager is ready. Add or remove domains to block.")
        current_domain_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lower_layout.addWidget(current_domain_label)

        self.main_layout.addWidget(lower_frame)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())




#self.lower_frame.setStyleSheet("background-color: red;")
#self.setStyleSheet("background-color: yellow;")
self.current_domain_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)