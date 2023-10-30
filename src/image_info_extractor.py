# image_info_extractor.py
from PIL import Image
from PIL.ExifTags import TAGS

class ImageInfoExtractor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.exif_data = {}
    
    def extract_exif(self):
        # Ouvrir l'image et extraire les données EXIF si elles existent
        pass

    def export_to_json(self):
        # Exportez les données EXIF au format JSON
        pass
