from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt

class MoveableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._old_pos = None

    # di chuyển giao diện
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self._old_pos:
            delta = event.globalPos() - self._old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self._old_pos = None