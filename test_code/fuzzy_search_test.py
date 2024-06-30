import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QListWidget
from fuzzywuzzy import fuzz

class DomainSearchApp(QWidget):
    def __init__(self, domains):
        super().__init__()
        self.domains = domains
        self.init_ui()
        self.populate_results_list()  # Populate the list when the app starts
    
    def init_ui(self):
        self.setWindowTitle('Domain Search')
        layout = QVBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('Type to search...')
        self.search_bar.textChanged.connect(self.update_search_results)
        layout.addWidget(self.search_bar)

        self.results_list = QListWidget()
        layout.addWidget(self.results_list)

        self.setLayout(layout)
        self.update_search_results('')
    
    def populate_results_list(self):
        for domain in self.domains:
            self.results_list.addItem(domain)
    
    def update_search_results(self, query):
        self.results_list.clear()
        for domain in self.domains:
            similarity_score = fuzz.partial_ratio(query.lower(), domain.lower())
            if similarity_score >= 70:  # Adjust this threshold as needed
                self.results_list.addItem(domain)

def main():
    initial_domains = ['example.com', 'example.net', 'example.org', 'domain.com', 'domain.net', 'domain.org', "charstar.ai", "itch.io", "character.ai", "opendns.com", "play.aidungeon.com", "aidungeon.com", "civitai.com", "newgrounds.com", "yandex.com"]
    app = QApplication(sys.argv)
    search_app = DomainSearchApp(initial_domains)
    search_app.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
