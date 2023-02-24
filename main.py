import sys
import PyQt6.QtWidgets as qw
from view import *
from model import *

def main() -> None:
    palette = Palette()
    tileData = TileData(32)
    app = qw.QApplication([])
    window = SuperSpiderWindow(palette, tileData)
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()