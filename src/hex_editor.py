from PySide6.QtWidgets import QTextEdit
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt
from PIL import Image

class HexEditor(QTextEdit):
    def __init__(self, raw_content_widget=None, hex_editor_widget=None, image_label=None):
        super().__init__()
        self.hex_view = ""  # Contiendra la représentation hexadécimale
        self.raw_content = ""  # Contiendra le contenu brut
        self.raw_content_widget = raw_content_widget
        self.hex_editor_widget = hex_editor_widget
        self.image_label = image_label

    def load_content(self, file_content):
        self.raw_content = file_content
        self.hex_view = self.generate_hex_view()
    
    def load_image_content(self, image_content):
        # Affichage du contenu brut (image) à droite
        #self.image_label.setScaledContents(True) #redimensionnement de l'image
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(image_content)
        self.image_label.setPixmap(pixmap)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        self.raw_content_widget.setLayout(layout)


    def generate_hex_view(self):
        # Initialiser une chaîne vide pour la représentation hexadécimale
        hex_data = ""

        # Parcourez chaque octet du contenu brut
        for byte in self.raw_content.encode('utf-8'):
            # Convertissez l'octet en une chaîne hexadécimale avec deux caractères (0x00 - 0xFF)
            hex_byte = format(byte, '02X')

            # Ajoutez la représentation hexadécimale à la chaîne hex_data
            hex_data += hex_byte + " "

        # Retournez la représentation hexadécimale
        return hex_data