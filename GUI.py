import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from image_down import download_images  # Import the function from image_download.py

# Define the main application class inheriting from QWidget
class ImageSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()  # Initialize the UI

    # Initialize the user interface
    def initUI(self):
        self.setWindowTitle('Image Search GUI')  # Set window title
        self.setGeometry(100, 100, 800, 600)  # Set window dimensions

        layout = QVBoxLayout()  # Create a vertical box layout

        # Create and configure the search input field
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText('Enter search term')
        layout.addWidget(self.search_input)

        # Create and configure the search button
        self.search_button = QPushButton('Search Images', self)
        self.search_button.clicked.connect(self.search_images)  # Connect button click to search_images method
        layout.addWidget(self.search_button)

        # Create and configure the list widget to display image paths
        self.image_list = QListWidget(self)
        layout.addWidget(self.image_list)

        # Create and configure the label to display the selected image
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)  # Center align the image
        layout.addWidget(self.image_label)

        self.setLayout(layout)  # Set the layout for the main window

    # Method to handle image search
    def search_images(self):
        search_term = self.search_input.text()  # Get the search term from input
        if not search_term:
            QMessageBox.warning(self, 'Error', 'Please enter a search term')  # Show warning if search term is empty
            return

        # Create a directory to save images based on the search term
        save_dir = f'data/{search_term.replace(" ", "_")}'
        os.makedirs(save_dir, exist_ok=True)

        try:
            # Download images using the download_images function
            image_paths = download_images(search_term, 10, save_dir)
            self.image_list.clear()  # Clear any existing items in the list
            self.image_paths = image_paths

            # Add downloaded image paths to the list widget
            for image_path in self.image_paths:
                self.image_list.addItem(image_path)

            # Connect list item click to the display_image method
            self.image_list.itemClicked.connect(self.display_image)

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to retrieve images: {e}')  # Show error message if download fails

    # Method to display the selected image
    def display_image(self, item):
        image_path = item.text()  # Get the image path from the clicked item
        pixmap = QPixmap(image_path)  # Create a QPixmap object from the image path
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))  # Set the pixmap to the label, keeping the aspect ratio

# Main block to run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)  # Create the application object
    ex = ImageSearchApp()  # Create an instance of the ImageSearchApp
    ex.show()  # Show the application window
    sys.exit(app.exec_())  # Execute the application
