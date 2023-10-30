# ui.py
from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QSplitter
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog
from .hex_editor import HexEditor # Importez la classe HexEditor
from .file_editor import FileEditor # Importez la classe FileEditor
import requests
from PIL import Image

class FileAnalyzerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Créez les composants graphiques pour afficher la représentation hexadécimale et le contenu brut
        self.hex_editor_widget = QtWidgets.QTextEdit(self)  # Composant pour la représentation hexadécimale
        self.raw_content_widget = QtWidgets.QTextEdit(self)  # Composant pour le contenu brut
        self.image_label = QtWidgets.QLabel()
        self.hex_editor = HexEditor(self.raw_content_widget, self.hex_editor_widget, self.image_label)
        

        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("File Analyzer")
        self.setGeometry(100, 100, 850, 650)

        # Créez un widget central pour contenir la division verticale
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        # Créez un diviseur vertical pour diviser l'écran
        splitter = QSplitter(Qt.Horizontal)

        # Créez un éditeur hexadécimal à gauche
        self.hex_editor_widget.setLineWrapMode(QTextEdit.WidgetWidth)
        splitter.addWidget(self.hex_editor_widget)
        # Créez une zone de texte pour le contenu brut à droite
        self.raw_content_widget.setLineWrapMode(QTextEdit.WidgetWidth)
        splitter.addWidget(self.raw_content_widget)
        # Ajoutez le diviseur au widget central
        layout = QtWidgets.QHBoxLayout(central_widget)
        layout.addWidget(splitter)
        ##layout.addWidget(self.image_label) Pour l'instant ça affiche l'image mais a voir pour mieux le faire

        self.image_label.setScaledContents(True) #redimensionnement de l'image
        # Créez des actions et des menus pour Charger, Enregistrer, etc.
        load_action = QAction("Charger Fichier", self)
        save_action = QAction("Enregistrer Fichier", self)
        open_url_action = QAction("Ouvrir URL", self)
        exit_action = QAction("Quitter", self)


        # Déclarez les booléens pour suivre les mises à jour des widgets hexa et brute
        self.updating_hex_view = False
        self.updating_raw_content = False

        ###############################################################
        # Connectez les actions à des méthodes appropriées

        load_action.triggered.connect(self.load_file)
        save_action.triggered.connect(self.save_file)
        open_url_action.triggered.connect(self.open_url)
        # Configurez le signal textChanged pour détecter les modifications dans le composant graphique hex_editor_widget
        self.hex_editor_widget.textChanged.connect(self.update_raw_content)
        # Configurez le signal textChanged pour détecter les modifications dans le composant graphique raw_content_widget
        self.raw_content_widget.textChanged.connect(self.update_hex_view)
        exit_action.triggered.connect(self.quit_app)

        # Créez un menu Fichier
        file_menu = self.menuBar().addMenu("Fichier")
        file_menu.addAction(load_action)
        file_menu.addAction(save_action)
        file_menu.addAction(open_url_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Créez un menu Aide
        help_menu = self.menuBar().addMenu("Aide")

        # Créez des boutons pour les autres fonctionnalités
        # Vous pouvez les ajouter à la fenêtre comme des widgets QPushButton

    def load_file(self):
        # Cette méthode sera appelée lorsque vous cliquez sur "Charger Fichier"
        # Vous pouvez implémenter ici la logique pour charger un fichier local
        options = QFileDialog.Options()

        file_path, _ = QFileDialog.getOpenFileName(self, "Charger un fichier", "", "Fichiers (*.*)", options=options)

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
                #self.raw_content_widget.clear()
                self.image_label.setFixedSize(200, 100)## Ok c'est bon mais je veux l'afficher dans lapartie de droite
                label_size = self.image_label.size()
                pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(pixmap)
                layout = QtWidgets.QVBoxLayout()
                layout.addWidget(self.image_label)
                self.raw_content_widget.setLayout(layout)
                #self.hex_editor.load_image_content(image_content)
                print(f"After loading image\n")
                # commande exiftool ici pour obtenir les données EXIF et les afficher dans un popup JSON.
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
        # Utilisez une boîte de dialogue de sauvegarde de fichier pour permettre à l'utilisateur de choisir l'emplacement de sauvegarde
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer le Fichier", "", "Tous les fichiers (*);;Fichiers texte (*.txt)", options=options)

        if file_path:
            # Récupérez le texte brut actuel depuis raw_content_widget
            raw_text = self.raw_content_widget.toPlainText()

            # Enregistrez le texte brut dans le fichier sélectionné
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(raw_text)
                QtWidgets.QMessageBox.information(self, "Sauvegarde Réussie", "Le fichier a été enregistré avec succès.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Erreur de Sauvegarde", f"Une erreur s'est produite lors de la sauvegarde : {str(e)}")

    def open_url(self):
            #Boîte de dialogue pour demander au user de saisir l'URL du fichier à ouvrir
        url, ok = QtWidgets.QInputDialog.getText(self, "Ouvrir URL", "Entrez l'URL du fichier :")

        if ok:
            try:
                # Effectuez une requête HTTP pour récupérer le contenu de l'URL
                response = requests.get(url)

                # Vérifiez si la requête a réussi
                if response.status_code == 200:
                    # Obtenez le contenu brut depuis la réponse HTTP
                    raw_text = response.text

                    # Mettez à jour le composant graphique raw_content_widget avec le contenu brut
                    self.raw_content_widget.setPlainText(raw_text)

                    # Mettez à jour la représentation hexadécimale
                    self.update_hex_view()
                else:
                    QtWidgets.QMessageBox.warning(self, "Erreur de Chargement", f"La requête a échoué avec le code d'état : {response.status_code}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Erreur de Chargement", f"Une erreur s'est produite lors du chargement : {str(e)}")

    def update_raw_content(self):
         # Mettez à jour le contenu brut lorsque le texte hexadécimal est modifié
        if not self.updating_hex_view:
            self.updating_raw_content = True
            # Mettez à jour le contenu brut lorsque le texte hexadécimal est modifié
            hex_text = self.hex_editor_widget.toPlainText()
            raw_text = self.convert_hex_to_raw(hex_text)

            # Mettez à jour le composant graphique raw_content_widget
            self.raw_content_widget.setPlainText(raw_text)

            # Mettez à jour les variables hex_view et raw_content dans la classe HexEditor
            self.hex_editor.hex_view = hex_text
            self.hex_editor.raw_content = raw_text
            # Réinitialisez le booléen
            self.updating_raw_content = False

    def convert_hex_to_raw(self, hex_text):
        # Implémentez la logique pour la conversion du texte hexadécimal en contenu brut
        # Vous devrez implémenter cette conversion en fonction de vos besoins
        # On sépare les espaces du fichier hex car entre chaque octet y'a un espace et pour convertir on en veux pas
        raw_text = bytes.fromhex(hex_text.replace(" ", "")).decode("utf-8")
        return raw_text
    
    def update_hex_view(self):
        # Si y'a pas de maj dans le contenue brute
        if not self.updating_raw_content:
            # Marquez la mise à jour en cours
            self.updating_hex_view = True
            # Mettez à jour la représentation hexadécimale lorsque le texte brut est modifié
            raw_text = self.raw_content_widget.toPlainText()
            hex_text = self.convert_raw_to_hex(raw_text)

            # Mettez à jour le composant graphique hex_editor_widget
            self.hex_editor_widget.setPlainText(hex_text)

            # Mettez à jour les variables hex_view et raw_content dans la classe HexEditor
            self.hex_editor.hex_view = hex_text
            self.hex_editor.raw_content = raw_text
            self.updating_hex_view = False

    def convert_raw_to_hex(self, raw_text):
        # Implémentez la logique pour la conversion du contenu brut en texte hexadécimal
        # Vous devrez implémenter cette conversion en fonction de vos besoins
        # Voici un exemple simple pour illustrer le concept
        hex_text = raw_text.encode("utf-8").hex()
        return " ".join(hex_text[i:i+2] for i in range(0, len(hex_text), 2))
    
    def quit_app(self):
        # Affichez une boîte de dialogue pour confirmer la sortie de l'application
        reply = QtWidgets.QMessageBox.question(self, "Quitter", "Êtes-vous sûr de vouloir quitter l'application ?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        # Si le user confirme la sortie, fermez l'application
        if reply == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()