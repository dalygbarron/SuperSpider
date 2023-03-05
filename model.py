import random, math
import PyQt6.QtCore as qc
from util import *

class Palette(qc.QObject):
    """A nice set of 256 2 byte colours"""
    _colours: bytearray = bytearray([0] * 256 * 2)
    _selectedRow: int = 0
    _selectedCol: int = 0
    changeData = qc.pyqtSignal()
    changeSelection = qc.pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        for x in range(16):
            for y in range(16):
                self.setColour(
                    y * 16 + x,
                    bytes([random.randint(0, 255), random.randint(0, 255)])
                )

    def setColour(self, index: int, value: bytes) -> None:
        """Updates the colour at the given index. Value needs to be in the 2
        byte correct format already."""
        self._colours[index * 2] = value[0]
        self._colours[index * 2 + 1] = value[1]
        self.changeData.emit()
    
    def getColour(self, index: int) -> bytes:
        """Gets the colour at the given index"""
        return bytes([self._colours[index * 2], self._colours[index * 2 + 1]])
    
    def select(self, row: int, col: int) -> None:
        """Sets the selected colour and palette"""
        oldRow = self._selectedRow
        oldCol = self._selectedCol
        self._selectedRow = row
        self._selectedCol = col
        self.changeSelection.emit(oldRow, oldCol)

    def getSelection(self) -> tuple[int, int]:
        """Tells you what palette row and item is selected"""
        return (self._selectedRow, self._selectedCol)
    
    def getActiveColour(self, index: int) -> bytes:
        """Gets the colour at the given 4 bit index for the currently selected
        palette."""
        index = (self._selectedRow * 16 + index) * 2
        return bytes([self._colours[index + 1], self._colours[index]])

class TileData(qc.QObject):
    """Represents a bunch of indexed tile data. Just stores each one as a byte
    which I know is a bit of a waste of memory but it means you could
    hypothetically export in different formats rather than building it around
    one specific one (maybe I'm just coping lol)."""
    TILE_SIZE = 8
    ROW_WIDTH = 16
    ROW_WIDTH_PIXELS = TILE_SIZE * ROW_WIDTH
    _pixels: bytearray
    _rows: int
    _selected = qc.QRect(0, 0, 2, 2)
    changeData = qc.pyqtSignal([int, int])
    changeSelection = qc.pyqtSignal()

    def __init__(self, rows):
        """Creates the tile data by specifying the number of rows of 8x8 tiles
        it will consist of."""
        super().__init__()
        self._pixels = bytearray(
            [0] * self.TILE_SIZE * self.TILE_SIZE * self.ROW_WIDTH * rows
        )
        self._rows = rows
        for x in range(self.ROW_WIDTH_PIXELS):
            for y in range(rows * self.TILE_SIZE):
                self._pixels[y * self.ROW_WIDTH_PIXELS + x] = random.randint(
                    0,
                    15
                )
    
    def getRows(self) -> int:
        """Tells you how many rows of 8x8 tiles there is in the tile data."""
        return self._rows
    
    def setPixel(self, x: int, y: int, value: int) -> None:
        """Sets the value of a given pixel in a fashion similar to how getPixel
        works."""
        self._pixels[y * self.ROW_WIDTH_PIXELS + x] = value
        self.changeData.emit(
            math.floor(x / self.TILE_SIZE),
            math.floor(y / self.TILE_SIZE)
        )
    
    def getPixel(self, x: int, y: int) -> int:
        """Gets you the pixel index at the given spot, fully in pixel
        coordinates with no regard for tiles."""
        return self._pixels[y * self.ROW_WIDTH_PIXELS + x]
        
    def setSelection(self, selection: qc.QRect) -> None:
        """Sets what 8x8 tiles are selected for editing"""
        self._selected.setCoords(*selection.getCoords())
        self.changeSelection.emit()

    def getSelection(self) -> qc.QRect:
        """Tells you what tiles are selected editing at this time"""
        return self._selected