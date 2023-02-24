import PyQt6.QtCore as qc

def expandColour(colour: bytes) -> tuple[int, int, int]:
    """Converts a two byte colour into a three byte colour in three ints"""
    return (
        (colour[0] & 0b1111100) << 1,
        (colour[1] & 0b11100000) >> 2 | (colour[0] & 0b11) << 6,
        (colour[1] & 0b11111) << 3
    )

def contractColour(r: int, g: int, b: int) -> bytes:
    """Takes three  ints representing a colour and turns them into 2 bytes"""
    return bytes([
        (((r >> 1) & 0b1111100) | ((g >> 6) & 0b11)) & 0x7f,
        (((g << 2) & 0b11100000) | ((b >> 3) & 0b11111)) & 0xff
    ])

def contractColourForRender(r: int, g: int, b: int) -> bytes:
    """Takes three  ints representing a colour and turns them into 2 bytes but
    with the colours reversed so the rendering thingy can use it."""
    return contractColour(b, g, r)

def fitInside(child: qc.QRectF, parent: qc.QRectF) -> qc.QRectF:
    """Takes the sizes of two different rectangles"""
    ratio = 1 / max(
        child.width() / parent.width(),
        child.height() / parent.height()
    )
    width = child.width() * ratio
    height = child.height() * ratio
    return qc.QRectF(
        abs(parent.width() - width) / 2,
        abs(parent.height() - height) / 2,
        width,
        height
    )