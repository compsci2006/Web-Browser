import sys
import json

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor

BOOKMARKS_FILE = "bookmarks.json"
HISTORY_FILE = "history.json"
HOME_URL = "https://www.google.com"

AD_BLOCK_LIST = [
    "ads", "doubleclick", "googlesyndication",
    "tracking", "analytics"
]

# ------------- Ad Blocker ---------------------
class AdBlocker(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString().lower()
        if any(ad in url for ad in AD_BLOCK_LIST):
            info.block(True)

# ------------- Web Browser ---------------------
class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Web Browser")
        self.setGeometry(100, 100, 1200, 800)

        self.bookmarks = self.load_json(BOOKMARKS_FILE)
        self.history = self.load_json(HISTORY_FILE)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setRequestInterceptor(AdBlocker())

        self.build_toolbar()
        self.add_new_tab(QUrl(HOME_URL))

    # ------------- User Interface ---------------------
    def build_toolbar(self):
        nav = QToolBar()
        self.addToolBar(nav)

        nav.addAction("Back", lambda: self.current().back())
        nav.addAction("Forward", lambda: self.current().forward())
        nav.addAction("Reload", lambda: self.current().reload())
        nav.addAction("Home", self.go_home)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate)
        nav.addWidget(self.url_bar)

        nav.addAction("Bookmarks", self.add_bookmark)
        nav.addAction("History", self.show_history)
        nav.addAction("Show Bookmarks", self.show_bookmarks)
        nav.addAction("Incognito", self.new_incognito_tab)
        nav.addAction("Summarize", self.summarize_page)

  # ------------- Tabs ---------------------
    def add_new_tab(self, url, incognito=False):
        profile = QWebEngineProfile() if incognito else self.profile
        page = QWebEnginePage(profile, self)

        browser = QWebEngineView()
        browser.setPage(page)
        browser.setUrl(url)

        i = self.tabs.addTab(browser, "Private" if incognito else "New Tab")
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl: self.update_url(qurl, browser))
        browser.loadFinished.connect(lambda: self.update_title(browser))
        browser.page().profile().downloadRequested.connect(self.handle_download)

    def new_incognito_tab(self):
        self.add_new_tab(QUrl(HOME_URL), incognito=True)

    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)

    def current(self):
        return self.tabs.currentWidget()

  # ------------- Navigation ---------------------
    def navigate(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.current().setUrl(QUrl(url))

    def go_home(self):
        self.current().setUrl(QUrl(HOME_URL))

    def update_url(self, qurl, browser):
        if browser == self.current():
            self.url_bar.setText(qurl.toString())
            self.save_history(qurl.toString())

    def update_title(self, browser):
        i = self.tabs.indexOf(browser)
        if i != -1:
            self.tabs.setTabText(i, browser.page().title())

  # ------------- Download Manager ---------------------
    def handle_download(self, download):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", download.path())
        if path:
            download.setPath(path)
            download.accept()

    # ------------- Bookmarks ---------------------
    def add_bookmark(self):
        url = self.current().url().toString()
        title = self.current().page().title()
        self.bookmarks.append({"title": title, "url": url})
        self.save_json(BOOKMARKS_FILE, self.bookmarks)
        QMessageBox.information(self, "Saved", "Bookmark added")

    def show_bookmarks(self):
        self.show_list("Bookmarks", self.bookmarks)

    # ------------- History ---------------------
    def save_history(self, url):
        self.history.append({"url": url, "time": QDateTime.currentDateTime().toString()})
        self.save_json(HISTORY_FILE, self.history)

    def show_history(self):
        self.show_list("History", self.history)

   # ------------- List Viewer ---------------------
    def show_list(self, title, data):
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        layout = QVBoxLayout()

        list_widget = QListWidget()
        for item in data:
            list_widget.addItem(item["url"])

        list_widget.itemClicked.connect(
            lambda item: self.current().setUrl(QUrl(item.text()))
        )

        layout.addWidget(list_widget)
        dlg.setLayout(layout)
        dlg.resize(400, 500)
        dlg.exec_()

    # ---------------- AI Summarizer ----------------
    def summarize_page(self):
        def handle_text(text):
            summary = (
                "AI Summarizer Placeholder\n\n"
                "This is where an LLM API would summarize:\n\n"
                + text[:800] + "..."
            )
            QMessageBox.information(self, "Page Summary", summary)

        self.current().page().toPlainText(handle_text)

    # ---------------- Utilities ----------------
    def load_json(self, file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except:
            return []

    def save_json(self, file, data):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)


# ---------------- Application Execution ----------------
app = QApplication(sys.argv)
window = Browser()
window.show()
sys.exit(app.exec_())

