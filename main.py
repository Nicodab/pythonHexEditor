#!/usr/bin/python
from src.file_editor import FileEditor
from src.file_info import FileInfo
from src.image_info_extractor import ImageInfoExtractor
from src.network_file_viewer import NetworkFileViewer
from src.ui import FileAnalyzerApp
from src.hex_editor import HexEditor
from PySide6 import QtWidgets
import sys

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = FileAnalyzerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()