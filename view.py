import PyQt6.QtWidgets as qw
import PyQt6.QtOpenGLWidgets as qglw
import PyQt6.QtGui as qg
from PyQt6.QtCore import Qt as qt
import PyQt6.QtCore as qc
from model import *
from util import *

class TileImageCache(qc.QObject):
    """Stores a cache of 8x8 tiles as images"""
    palette: Palette
    tileData: TileData
    images: list[list[qg.QImage]]
    change = qc.pyqtSignal()

    def __init__(self, palette: Palette, tileData: TileData):
        """Gives it the palette and tile data it uses to render the tiles."""
        super().__init__()
        self.palette = palette
        self.tileData = tileData
        self.images = [[None] * tileData.getRows()] * TileData.ROW_WIDTH
        palette.change.connect(self._updateAllTiles)
        for x in range(TileData.ROW_WIDTH):
            for y in range(tileData.getRows()):
                self.images[x][y] = qg.QImage(
                    TileData.TILE_SIZE,
                    TileData.TILE_SIZE,
                    qg.QImage.Format.Format_RGB555
                )
                self._updateTile(x, y)
    
    def _updateAllTiles(self) -> None:
        """Updates all the tiles when necessary"""
        for x in range(TileData.ROW_WIDTH):
            for y in range(self.tileData.getRows()):
                self._updateTile(x, y)
    
    def _updateTile(self, x: int, y: int) -> None:
        """Recreates the data in a given tile's image based on the latest
        info"""
        image = self.images[x][y]
        data = image.bits()
        data.setsize(TileData.TILE_SIZE * TileData.TILE_SIZE * 2)
        for ix in range(TileData.TILE_SIZE):
            for iy in range(TileData.TILE_SIZE):
                index = self.tileData.getPixel(
                    x * TileData.TILE_SIZE + ix,
                    y * TileData.TILE_SIZE + iy
                )
                colour = self.palette.getActiveColour(index)
                loc = iy * TileData.TILE_SIZE * 2 + ix * 2
                data[loc:loc + 2] = colour
        self.change.emit()
    
    def getImage(self, x: int, y: int) -> qg.QImage:
        """Gets the corresponding image for this location"""
        return self.images[x][y]

class PaletteRenderer(qw.QWidget):
    """Does the actual rendering of the palette"""
    palette: Palette

    def __init__(self, palette: Palette):
        super().__init__()
        self.palette = palette
        self.mouseReleaseEvent = self._clicked
        palette.change.connect(self.update)

    def _clicked(self, event: qg.QMouseEvent) -> None:
        if event.button() == qt.MouseButton.LeftButton:
            row = math.floor(event.position().y() / 16)
            self.palette.setActive(row)
    
    def paintEvent(self, event: qg.QPaintEvent) -> None:
        painter = qg.QPainter()
        painter.begin(self)
        brush = qg.QBrush()
        brush.setStyle(qt.BrushStyle.SolidPattern)
        for x in range(16):
            for y in range(16):
                colour = self.palette.getColour(y * 16 + x % 16)
                brush.setColor(qg.QColor(*expandColour(colour)))
                painter.setBrush(brush)
                painter.fillRect(x * 16, y * 16, 16, 16, painter.brush())
        brush.setStyle(qt.BrushStyle.NoBrush)
        painter.setBrush(brush)
        painter.drawRect(0, self.palette.getActive() * 16, 16 * 16, 16)
        painter.end()

class TileDataRenderer(qw.QWidget):
    """Does the actual rendering of the tile data"""
    tileData: TileData
    palette: Palette
    tileCache: TileImageCache
    image: qg.QImage

    def __init__(
        self,
        tileData: TileData,
        palette: Palette,
        tileCache: TileImageCache
    ):
        super().__init__()
        self.setMinimumSize(
            TileData.ROW_WIDTH_PIXELS * 2,
            TileData.TILE_SIZE * tileData.getRows() * 2
        )
        self.tileData = tileData
        self.palette = palette
        self.tileCache = tileCache
        tileCache.change.connect(self.update)

    def paintEvent(self, event: qg.QPaintEvent) -> None:
        painter = qg.QPainter()
        painter.begin(self)
        rect = qc.QRectF()
        for x in range(TileData.ROW_WIDTH):
            for y in range(self.tileData.getRows()):
                rect.setCoords(
                    x * TileData.TILE_SIZE * 2,
                    y * TileData.TILE_SIZE * 2,
                    (x + 1) * TileData.TILE_SIZE * 2,
                    (y + 1) * TileData.TILE_SIZE * 2
                )
                painter.drawImage(rect, self.tileCache.getImage(x, y))
        painter.end()

class TileEditor(qw.QWidget):
    """This is where you have got a zoomed in view of a single or set of tiles
    and you can edit it"""
    palette: Palette
    tileData: TileData
    tileCache: TileImageCache

    def __init__(
        self,
        palette: Palette,
        tileData: TileData,
        tileCache: TileImageCache
    ):
        super().__init__()
        self.tileData = tileData
        self.palette = palette
        self.tileCache = tileCache
        tileCache.change.connect(self.update)
        self.setMinimumSize(256, 256)

    def paintEvent(self, event: qg.QPaintEvent) -> None:
        dimensions = self.geometry()
        rect = fitInside(qc.QRectF(0, 0, TileData.TILE_SIZE, TileData.TILE_SIZE), dimensions)
        painter = qg.QPainter()
        painter.begin(self)
        painter.drawImage(rect, self.tileCache.getImage(0, 0))
        painter.end()

class SuperSpiderWindow(qw.QMainWindow):
    """Main window of tha program"""

    def __init__(self, palette: Palette, tileData: TileData):
        super().__init__()
        self.setWindowTitle("Super Spider v69")
        self._setupMenu()
        tileCache = TileImageCache(palette, tileData)
        widget = qw.QWidget()
        layout = qw.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        vSplit = qw.QFrame()
        sideLayout = qw.QVBoxLayout()
        sideLayout.setContentsMargins(0, 0, 0, 0)
        visual = EditorView(tileData, palette, tileCache)
        paletteView = PaletteView(palette)
        tile = TileView(tileData, palette, tileCache)
        vSplit.setLayout(sideLayout)
        vSplit.setSizePolicy(
            qw.QSizePolicy.Policy.Maximum,
            qw.QSizePolicy.Policy.Expanding
        )
        visual.setMinimumSize(100, 100)
        sideLayout.addWidget(tile)
        sideLayout.addWidget(paletteView)
        layout.addWidget(vSplit)
        layout.addWidget(visual)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _setupMenu(self) -> None:
        """Sets up the menus that go at the top of the screen/window."""
        menuBar = self.menuBar()
        fileMenu = qw.QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        exitAct = qg.QAction(qg.QIcon('exit.png'), '&Vibe', self)
        exitAct.setShortcut('Ctrl+V')
        exitAct.setStatusTip('Vibe Bigly')
        exitAct.triggered.connect(qw.QApplication.instance().quit)
        fileMenu.addAction(exitAct)

class PaletteView(qw.QFrame):
    """Widget that lets you view/open/edit/select items from palettes"""
    visual: PaletteRenderer

    def __init__(self, palette: Palette):
        super().__init__()
        layout = qw.QVBoxLayout()
        self.visual = PaletteRenderer(palette)
        button = qw.QPushButton("Aids aids aids")
        self.visual.setMinimumSize(256, 256)
        layout.addWidget(self.visual)
        layout.addWidget(button)
        self.setLayout(layout)
        self._refresh()

    def _refresh(self) -> None:
        """Refreshes the rendered palette data"""
        self.visual

class TileView(qw.QFrame):
    """Widget that lets you view/open/select tile data for editing"""

    def __init__(
        self,
        tileData: TileData,
        palette: Palette,
        tileCache: TileImageCache
    ):
        super().__init__()
        layout = qw.QVBoxLayout()
        scroller = qw.QScrollArea()
        pic = TileDataRenderer(tileData, palette, tileCache)
        button = qw.QPushButton("Aids aids aids")
        scroller.setWidget(pic)
        scroller.setVerticalScrollBarPolicy(qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroller.setHorizontalScrollBarPolicy(qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(scroller)
        layout.addWidget(button)
        self.setLayout(layout)

class EditorView(qw.QFrame):
    """Widget that lets you look at a zoomed in version of the tile and draw
    on it and select tools to draw on it with"""
    
    def __init__(
        self,
        tileData: TileData,
        palette: Palette,
        tileCache: TileImageCache
    ):
        super().__init__()
        layout = qw.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        pic = TileEditor(tileData, palette, tileCache)
        tools = ToolView()
        layout.addWidget(tools)
        layout.addWidget(pic)
        self.setLayout(layout)

class ToolView(qw.QFrame):
    """Bar that contains the tools you can utilise like pen, fill, etc"""

    def __init__(self):
        super().__init__()
        layout = qw.QVBoxLayout()
        layout.setAlignment(qt.AlignmentFlag.AlignTop)
        layout.addWidget(qw.QPushButton("a"))
        layout.addWidget(qw.QPushButton("b"))
        layout.addWidget(qw.QPushButton("c"))
        self.setLayout(layout)
        self.setSizePolicy(
            qw.QSizePolicy.Policy.Maximum,
            qw.QSizePolicy.Policy.Expanding
        )