from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QSplitter
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog
from .hex_editor import HexEditor
from .file_editor import FileEditor
import requests
import json
from PySide6.QtCore import QPoint
from PIL import Image, ExifTags

HTTP_HEADERS_TO_DISPLAY = ["Server", "Date", "Content-Type", "Content-Length", "Content-Encoding", "Accept-Ranges"]

class FileAnalyzerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Composants graphiques, la représentation hexadécimale et le contenu brut
        self.hex_editor_widget = QtWidgets.QTextEdit(self)
        self.raw_content_widget = QtWidgets.QTextEdit(self)
        self.image_label = QtWidgets.QLabel()
        self.image_info_label = QtWidgets.QLabel()
        self.image_exif_label = QtWidgets.QLabel()
        self.http_header_label = QtWidgets.QLabel("HTTP - Header")
        self.http_header_text = QtWidgets.QTextEdit()
        self.hex_editor = HexEditor(self.raw_content_widget, self.hex_editor_widget, self.image_label)
        self.layout_for_image = None
        self.help_action = None
        self.current_file_path = ""
        self.json_data = None
        self.exif_dict = {} ## Récupérer ce exif_dict pour le réutiliser dans l'export au format json 

        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("File Analyzer")
        self.setGeometry(100, 100, 850, 650)

        # Widget central pour contenir la division verticale
        central_widget = QtWidgets.QWidget(self)
        
        http_header_widget = QtWidgets.QWidget()
        http_header_widget.setFixedHeight(180)
        # QVBoxLayout pour organiser les composants verticalement
        http_layout = QtWidgets.QVBoxLayout()
        # Http Layout section
        # On place avant le splitter qui contiendra la partie gauche et droite
        self.http_header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
         # Style du QLabel
        self.http_header_label.setFixedHeight(40)
        self.http_header_label.setStyleSheet("border-style: solid; border-width: 1px; border-color: black;")
        
        # Composant d'affichage de texte HTTP
        http_text = QTextEdit()
        http_text.setPlainText("Affichage du texte de l'en-tête HTTP ici.")
        http_text.setReadOnly(True)
        self.http_header_text = http_text
        http_layout.addWidget(self.http_header_label)
        http_layout.addWidget(self.http_header_text)
        
        # On Applique le layout au widget http_header_widget
        http_header_widget.setLayout(http_layout)
        # Diviseur vertical pour diviser l'écran
        splitter = QSplitter(Qt.Horizontal)

        # Editeur hexadécimal à gauche
        self.hex_editor_widget.setLineWrapMode(QTextEdit.WidgetWidth)

        splitter.addWidget(self.hex_editor_widget)
        # Zone de texte pour le contenu brut à droite
        self.raw_content_widget.setLineWrapMode(QTextEdit.WidgetWidth)
        splitter.addWidget(self.raw_content_widget)

        # Diviseur au widget central
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.addWidget(http_header_widget) # c'est pas un self, à voir comment mettre tout ça dans une classe
        layout.addWidget(splitter)
        
        self.setCentralWidget(central_widget)

        self.image_label.setScaledContents(True) #redimensionnement de l'image
        # QActions pour le menu Fichier
        load_action = QAction("Charger Fichier", self)
        save_action = QAction("Enregistrer Fichier", self)
        open_url_action = QAction("Ouvrir URL", self)
        exit_action = QAction("Quitter", self)
        self.help_action = QAction("Aide", self)


        # Déclarez les booléens pour suivre les mises à jour des widgets hexa et brute
        self.updating_hex_view = False
        self.updating_raw_content = False

        ###############################################################
        # Connectez les actions à des méthodes appropriées
        # Bouton pour afficher les informations EXIF
        self.exif_button = QtWidgets.QPushButton("Afficher EXIF") # self pour le réutiliser autrepart
        self.export_button = QtWidgets.QPushButton("Export") # bouton pour exporter au  format json
        self.export_button.clicked.connect(self.export_exif)
        self.exif_button.clicked.connect(self.show_exif_info)
        
        load_action.triggered.connect(self.load_file)
        save_action.triggered.connect(self.save_file)
        open_url_action.triggered.connect(self.open_url)
        exit_action.triggered.connect(self.quit_app)
        self.help_action.triggered.connect(self.show_help)
        # Config le signal textChanged pour détecter les modifications dans le composant graphique hex_editor_widget
        self.hex_editor_widget.textChanged.connect(self.update_raw_content)
        # Config le signal textChanged pour détecter les modifications dans le composant graphique raw_content_widget
        self.raw_content_widget.textChanged.connect(self.update_hex_view)
        

        # Menu Fichier
        file_menu = self.menuBar().addMenu("Fichier")
        file_menu.addAction(load_action)
        file_menu.addAction(save_action)
        file_menu.addAction(open_url_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        file_menu.addAction(self.help_action)

    def load_file(self):
        # méthode appelé par l'action "Charger Fichier"
        options = QFileDialog.Options()

        file_path, _ = QFileDialog.getOpenFileName(self, "Charger un fichier", "", "Fichiers (*.*)", options=options)
        self.current_file_path = file_path
        if file_path:
            #Extension du fichier: image, texte, etc...
            file_extension = file_path.split(".")[1].lower()
            print(f"extension: {file_extension}\n")
            # Si image
            if file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                print(f"Before loading image\n")
                with open(file_path, 'rb') as file:
                    image_content = file.read()
                self.raw_content_widget.clear()
                pixmap = QtGui.QPixmap()
                pixmap.loadFromData(image_content)
                # Largeur et hauteur du parent
                image_label_parent_width = self.raw_content_widget.width()
                image_label_parent_height = self.raw_content_widget.height()
                self.image_label.setFixedSize(image_label_parent_width/2, image_label_parent_height/2) ## Ok c'est bon mais je veux l'afficher dans lapartie de droite
                label_size = self.image_label.size()
                pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(pixmap)
                self.layout_for_image = QtWidgets.QVBoxLayout()
                self.layout_for_image.addWidget(self.exif_button, alignment=Qt.AlignCenter)
                self.layout_for_image.addWidget(self.image_label, alignment=Qt.AlignCenter)
                self.raw_content_widget.setLayout(self.layout_for_image)
                ################################################################
                # on utilise l'instance de HexEditor pour charger le contenu du fichier
                self.hex_editor.load_content(image_content, True) # True pour charger le contenue hexa de l'image
                
                # Maj des zones de texte hex_editor (et raw_content?)
                self.hex_editor_widget.setPlainText(self.hex_editor.hex_view)
                ###################################################
                # Ouverture de l'image avec Pillow
                print(f"file_path: {file_path}")
                with Image.open(file_path) as img:
                    # Métadonnées
                    #meta_values = img.info.values()
                    #print(meta_values)
                    
                    image_info = img.info
                    # Exemple d'informations que vous pouvez extraire
                    image_size = len(img.tobytes())  # Poids de l'image en octets
                    image_mode = img.mode  # Mode de l'image
                    date_modification = image_info.get("DateTime") or image_info.get("DateTimeOriginal")
                    # Maintenant, vous pouvez afficher ces informations dans votre interface utilisateur
                    # Mise à jour du texte dans le QLabel 
                    self.image_info_label.setText(f"Poids de l'image: {image_size} octets\n"
                                            f"Mode de l'image: {image_mode}\nDate de modification: {date_modification}")
                    #self.image_info_label.setLineWidth(3)
                    self.image_info_label.setStyleSheet("border-radius: 10px; border-style: solid; border-width: 1px; border-color: black;")
                    self.layout_for_image.addWidget(self.image_info_label, alignment=Qt.AlignCenter)
                    #layout_json = QtWidgets.QVBoxLayout()
                    #layout_json.addWidget(self.export_button)
                    self.raw_content_widget.setLayout(self.layout_for_image)
                #self.hex_editor.load_image_content(image_content)
                #self.hex_editor_widget.setPlainText(self.hex_editor.hex_view)
                print(f"After loading image\n")
            # Pas image
            else:
                with open(file_path, "r", encoding="utf-8") as file:
                    file_content = file.read()

                    # Utilisez l'instance de HexEditor pour charger le contenu du fichier
                    self.hex_editor.load_content(file_content)
                    # Mettez à jour les zones de texte hex_editor et raw_content
                    self.hex_editor_widget.setPlainText(self.hex_editor.hex_view)
                    self.raw_content_widget.setPlainText(self.hex_editor.raw_content)

    def save_file(self):
        # Boîte de dialogue de sauvegarde
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer le Fichier", "", "Tous les fichiers (*);;Fichiers texte (*.txt)", options=options)

        if file_path:
            # Texte brut actuel
            raw_text = self.raw_content_widget.toPlainText()

            # Enregistrez le texte brut dans le fichier sélectionné
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(raw_text)
                QtWidgets.QMessageBox.information(self, "Sauvegarde Réussie", "Le fichier a été enregistré avec succès.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Erreur de Sauvegarde", f"Une erreur s'est produite lors de la sauvegarde : {str(e)}")

    def open_url(self):
        if self.hex_editor.isClean() == False:
            print("PAAAAAAAAAAAAAAAAAAAS CLEEEEEEEEEEEEEEEAN")
            self.hex_editor.cleanViews()
            self.hex_editor_widget.setPlainText(self.hex_editor.hex_view)
            self.hex_editor_widget.setPlainText(self.hex_editor.raw_content)
            self.cleanRawContentLayout()

        #B oîte de dialogue pour demander au user de saisir l'URL du fichier à ouvrir
        url, ok = QtWidgets.QInputDialog.getText(self, "Ouvrir URL", "Entrez l'URL du fichier :")

        if ok:
            try:
                # Requête HTTP pour récupérer le contenu de l'URL
                response = requests.get(url)
                headers = response.headers
                http_header_content = ""
                for key, value in headers.items():
                    # Si le header HTTP fait partie de la liste 'importante des headers'
                    if key in HTTP_HEADERS_TO_DISPLAY:
                        http_header_content += f"{key} : {value}\n"
                
                # Maj du composant graphique http_header_text 
                self.http_header_text.setPlainText(http_header_content)
                
                # Si la requête a réussi
                if response.status_code == 200:
                    # Colorier en vert si c'est un succès
                    self.http_header_label.setStyleSheet("border-style: solid; border-width: 1px; border-color: green;")
                    # Obtention du contenu brut depuis la réponse HTTP
                    raw_text = response.text

                    # maj du composant graphique raw_content_widget avec le contenu brut
                    self.raw_content_widget.setPlainText(raw_text)

                    # maj pour la représentation hexadécimale
                    self.update_hex_view()
                else:
                    self.http_header_label.setStyleSheet("border-style: solid; border-width: 1px; border-color: red;")
                    # Rouge si c'est pas un succès
                    QtWidgets.QMessageBox.warning(self, "Erreur de Chargement", f"La requête a échoué avec le code d'état : {response.status_code}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Erreur de Chargement", f"Une erreur s'est produite lors du chargement : {str(e)}")

    def update_raw_content(self):
         # Maj du contenu brut lorsque le texte hexadécimal est modifié
        if not self.updating_hex_view:
            self.updating_raw_content = True
            # Maj du contenu brut lorsque le texte hexadécimal est modifié
            hex_text = self.hex_editor_widget.toPlainText()
            raw_text = self.convert_hex_to_raw(hex_text)

            # Maj du composant graphique raw_content_widget
            self.raw_content_widget.setPlainText(raw_text)

            # Maj des variables hex_view et raw_content, attributs de la classe HexEditor
            self.hex_editor.hex_view = hex_text
            self.hex_editor.raw_content = raw_text
            # Réinitialisation du booléen
            self.updating_raw_content = False

    def convert_hex_to_raw(self, hex_text):
        # On sépare les espaces du fichier hex car entre chaque octet y'a un espace et pour convertir on en veux pas
        raw_text = bytes.fromhex(hex_text.replace(" ", "")).decode("utf-8")
        return raw_text

    def update_hex_view(self):
        # Si y'a pas de maj dans le contenue brute
        if not self.updating_raw_content:
            # Marquage la mise à jour en cours
            self.updating_hex_view = True
            # Maj de la représentation hexadécimale lorsque le texte brut est modifié
            raw_text = self.raw_content_widget.toPlainText()
            hex_text = self.convert_raw_to_hex(raw_text)

            # Maj du composant graphique hex_editor_widget
            self.hex_editor_widget.setPlainText(hex_text)

            # Maj des variables hex_view et raw_content dans la classe HexEditor
            self.hex_editor.hex_view = hex_text
            self.hex_editor.raw_content = raw_text
            self.updating_hex_view = False

    def convert_raw_to_hex(self, raw_text):
        hex_text = raw_text.encode("utf-8").hex()
        return " ".join(hex_text[i:i+2] for i in range(0, len(hex_text), 2))
    

    def quit_app(self):
        reply = QtWidgets.QMessageBox.question(self, "Quitter", "Êtes-vous sûr de vouloir quitter l'application ?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        # Si le user confirme la sortie, fermez l'application
        if reply == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()

    def show_exif_info(self):
        if self.current_file_path:
            # Utilisation d'exiftool pour extraire les informations EXIF
            exif_info = self.extract_exif_info(self.current_file_path)

            if exif_info:
                self.show_exif_info_to_user(exif_info)
    
    def extract_exif_info(self, file_path):
        try:
            print("Extract 1\n")
            with Image.open(file_path) as img:
                exif_info = img.getexif()  # Récupération des informations EXIF
                
                if exif_info:
                    print("Info de l'image pas exif\n")
                    # On récupère les métadonnées basique de l'image (sans le exif)
                    exif_dict = {
                        "Filename": img.filename,
                        "Image Size": img.size,
                        "Image Height": img.height,
                        "Image Width": img.width,
                        "Image Format": img.format,
                        "Image Mode": img.mode,
                        "Image is Animated": getattr(img, "is_animated", False),
                        "Frames in Image": getattr(img, "n_frames", 1)
                    }

                    if (len(list(exif_info.values())) == 0):
                        print("No exif data in this image\n")
                    else:
                        for tag, value in exif_info.items():
                            tag_name = ExifTags.TAGS.get(tag, tag)
                            exif_dict[tag_name] = value
                            print(f"{tag_name:25}: {value}")

                    self.exif_dict = exif_dict ## self pour l'utiliser dans la f° construct_json_format
                    return exif_dict # On retourne un dictionnaire construi avec les infos de l'image ainsi que ses données exif si y'en a
                else:
                    print("exif_info = img.getefix() ne renvoi rien\n")
                    exif_dict = {
                        "Filename": img.filename,
                        "Image Size": img.size,
                        "Image Height": img.height,
                        "Image Width": img.width,
                        "Image Format": img.format,
                        "Image Mode": img.mode,
                        "Image is Animated": getattr(img, "is_animated", False),
                        "Frames in Image": getattr(img, "n_frames", 1)
                    }
                    if exif_dict is not None:
                        self.exif_dict = exif_dict ## self pour l'utiliser dans la f° construct_json_format
                        return exif_dict
                    else:
                        return None
        except Exception as e:
            print(f"An error occurred while extracting EXIF information: {str(e)}")
            return None
    
    def show_exif_info_to_user(self, exif_info):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Informations EXIF")
        dialog.setGeometry(100, 100, 400, 400)

        self.json_data = QtWidgets.QTextEdit(dialog)
        self.json_data.setGeometry(10, 10, 380, 380)

        layout_json = QtWidgets.QVBoxLayout()
        layout_json.addWidget(self.export_button, alignment=Qt.AlignBottom)
        self.json_data.setLayout(layout_json)

        exif_info_str = "{\n"
        for key, value in exif_info.items():
            exif_info_str += f'"{key}": "{value}"\n'
        exif_info_str += "}" # On ferme l'accolade du dico pour le mettre dans un str

        self.json_data.setPlainText(exif_info_str)

        dialog.exec()

    def export_exif(self):
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.setDefaultSuffix(".json")

        # Si la boîte est ouverte
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            # Si y'a eu un fichier de sélectionné
            if selected_file:
                with open(selected_file, 'w') as file:
                    # On prend le dico des données exif et on l'enregistre dans le json
                    json.dump(self.exif_dict, file, indent=4)

    def cleanRawContentLayout(self):
        # Suppression des éléments du layout
        while self.layout_for_image.count():
            item = self.layout_for_image.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            del item

        # Vérifier que le layout est vide
        assert self.layout_for_image.count() == 0

        # Suppression du layout du widget parent
        #self.raw_content_widget.setLayout(None) A VOIR SI ONREMET CA 
    
    def show_help(self):
        
        if self.help_action is not None:            
            # création d'une instance de la fenêtre d'aide et affichez-la
            help_dialog = HelpDialog()
            help_dialog.exec_()

class HelpDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        texte_aide_str = "Bienvenue sur sur HexEditor\nVous trouverez les différentes fonctionnalitées de cette application dans le menu 'Fichier':\n-  Charger fichier: choisissez un fichier localement pour pouvoir voir ou miodifier ses données.\n-  Enregistrer Ficher: Permet dechoisir où sauvergarder le fichier modifié sous une nouvelle appelation\n-  Ouvrir URL: Cette option permet de récupérer un fichier depuis un URL.\n   L'encadrement de Headers HTTP se colorie en Vert si la réponse du server 200 et se colorie en rouge sinon. De    plus, vous aurez les en-têtes HTTP de la réponse dans l'encadrement Juste en dessous de 'HTTP - HEADERS'.\n-  Quitter: Permet de sortir de l'application. Il est possible également d'appuyer sur la croix en haut à droite\n\n\
            \rRemarque: lors du chargement d'un fichier image en local, nous voyons son contenu visible, son poids, sa taille, etc, ...\r\n\
            \rUn bouton 'Afficher Exif' permet alors de voir les données exif de l'image.\nCes derniers apparaitront dans une nouvelle fenêtre à partir de laquelle vous pourrez cliquer sur le bouton 'Export Exif' afin de sauvergarder au format json le contenu exif."

        self.setWindowTitle("Aide")
        self.setGeometry(100, 100, 800, 600)

        layout = QtWidgets.QVBoxLayout()

        self.help_browser = QtWidgets.QTextBrowser()
        self.help_browser.setPlainText(texte_aide_str)
        layout.addWidget(self.help_browser)

        self.setLayout(layout)