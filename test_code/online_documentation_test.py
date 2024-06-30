import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView

class WebPageViewer(QMainWindow):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("Web Page Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create a QWebEngineView instance
        self.webview = QWebEngineView()

        # Convert the URL string to a QUrl object
        url = QUrl(url)

        # Load the specified URL
        self.webview.load(url)

        # Add the QWebEngineView to the layout
        layout.addWidget(self.webview)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Specify the URL you want to display
    url = "https://cbgithub7.github.io/Brave-Domain-Manager/"

    window = WebPageViewer(url)
    window.show()

    sys.exit(app.exec_())
