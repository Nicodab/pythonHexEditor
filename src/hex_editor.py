from PySide6.QtWidgets import QTextEdit
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt
from PIL import Image

class HexEditor(QTextEdit):
    def __init__(self, raw_content_widget=None, hex_editor_widget=None, image_label=None):
        super().__init__()
        self.hex_view = ""  # Contenu de la représentation hexadécimale
        self.raw_content = ""  # Contenu brut
        self.raw_content_widget = raw_content_widget
        self.hex_editor_widget = hex_editor_widget
        self.image_label = image_label

    def load_content(self, file_content, isImage:bool=False):
        self.raw_content = file_content
        self.hex_view = self.generate_hex_view(isImage=isImage)
    
    def load_image_content(self, image_content):
        # Affichage du contenu brut (image) à droite
        #self.image_label.setScaledContents(True) #redimensionnement de l'image
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(image_content)
        self.image_label.setPixmap(pixmap)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        self.raw_content_widget.setLayout(layout)


    def generate_hex_view(self, isImage:bool=False):
        
        if isImage is True:
            # Conversion de self.raw_content en un string
            raw_text = self.raw_content
            # conversion la chaîne de caractères en une représentation hexadécimale
            hex_text = " ".join(f"{byte:02X}" for byte in raw_text)

            return hex_text
        
        else:
            hex_data = ""
            # Parcours de chaque octet du contenu brut
            for byte in self.raw_content.encode('utf-8'):
                # Conversion de l'octet en une chaîne hexadécimale de deux caractères (0x00 - 0xFF)
                hex_byte = format(byte, '02X')

                # l'hexa à la chaîne hex_data
                hex_data += hex_byte + " "

            return hex_data
        
    def cleanViews(self):
        self.hex_view = ""
        self.raw_content = ""
        if self.image_label is not None:
            self.image_label.clear()
            #self.image_label = None
            #self.image_label = QtWidgets.QLabel()
            

    
    def isClean(self):
        if self.hex_view is not "" or self.raw_content is not "":
            return False
        if self.hex_view is "" and self.raw_content is "":
            return True
        return False