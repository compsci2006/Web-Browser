# Import required PyQt5 modules for GUI components, core functionality,
# and the web engine used to render web pages

# The GUI import is not necessary for this. You don't have to have it
# The web application still works without it 

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *

"""
    A simple web browser built using PyQt5.
    Provides basic navigation features such as URL input,
    back, forward, and page loading.
    """

class MyWebBrowser():
    def __init__(self):
        # Create the main application window
        self.window = QWidget()
        self.window.setWindowTitle("Google Web Browser")

        # Create vertical and horizontal layouts
        self.layout = QVBoxLayout()     # Main layout
        self.horizontal = QHBoxLayout() # Top navigation bar layout

        # URL input bar where the user types the website address
        self.url_bar = QTextEdit()
        self.url_bar.setMaximumHeight(30)

        # "Go" button to load the entered URL
        self.go_btn = QPushButton("Go")
        self.go_btn.setMinimumHeight(30)

        # Back navigation button
        self.back_btn = QPushButton("<")
        self.back_btn.setMinimumHeight(30)

        # Forward navigation button
        self.forward_btn = QPushButton(">")
        self.forward_btn.setMinimumHeight(30)

        # Add widgets to the horizontal navigation bar
        self.horizontal.addWidget(self.url_bar)
        self.horizontal.addWidget(self.go_btn)
        self.horizontal.addWidget(self.back_btn)
        self.horizontal.addWidget(self.forward_btn)

        # Web view widget used to display web pages
        self.browser = QWebEngineView()

        # Connect button clicks to their respective functions
        self.go_btn.clicked.connect(
            lambda: self.navigate(self.url_bar.toPlainText())
        )
        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)

        # Add navigation bar and browser view to the main layout
        self.layout.addLayout(self.horizontal)
        self.layout.addWidget(self.browser)

        # Load Google as the default home page
        self.browser.setUrl(QUrl("http://www.google.com"))

        # Apply layout to the window and display it
        self.window.setLayout(self.layout)
        self.window.show()

        """
        Navigates to the given URL.
        Automatically adds 'http://' if missing.
        """

    def navigate(self, url):
        if not url.startswith("http"):
            url = "http://" + url
            self.url_bar.setText(url)

        # Load the requested URL in the browser
        self.browser.setUrl(QUrl(url))

# Create the application instance
app = QApplication([])

# Create and display the browser window
window = MyWebBrowser()

# Start the application event loop
app.exec_()
