import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QListWidget, QAbstractItemView

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search_prefix(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return self._collect_words(node, prefix)

    def _collect_words(self, node, prefix):
        words = []
        if node.is_end_of_word:
            words.append(prefix)
        for char, child_node in node.children.items():
            words.extend(self._collect_words(child_node, prefix + char))
        return words

class DomainSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Domain Search')
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Domains")
        self.search_bar.textChanged.connect(self.updateListView)
        self.layout.addWidget(self.search_bar)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.NoSelection)
        self.layout.addWidget(self.list_widget)

        self.setLayout(self.layout)

        self.trie = Trie()
        self.initializeTrie()
        self.updateListView()

    def initializeTrie(self):
        # Fetch existing domains or use hardcoded example
        existing_domains = ["example.com", "example.net", "example.org", "test.com", "testing.com", "charstar.ai", "itch.io", "character.ai", "opendns.com", "play.aidungeon.com", "aidungeon.com", "civitai.com", "e621.net", "luscious.net", "sex.com", "literotica.com", "imagefap.com", "newgrounds.com", "yandex.com"]
        for domain in existing_domains:
            self.trie.insert(domain.lower())  # Insert domains in lowercase to handle case-insensitive search

    def updateListView(self):
        search_text = self.search_bar.text().lower()
        matching_domains = self.trie.search_prefix(search_text)

        if search_text.startswith('.') and len(search_text) > 1:  # Check if search text starts with a dot
            tld = search_text[1:]  # Remove the dot before searching
            filtered_domains = [domain for domain in matching_domains if domain.endswith('.' + tld)]
            self.list_widget.clear()
            for domain in filtered_domains:
                self.list_widget.addItem(domain)
        else:
            self.list_widget.clear()
            for domain in matching_domains:
                self.list_widget.addItem(domain)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DomainSearchApp()
    ex.show()
    sys.exit(app.exec_())
