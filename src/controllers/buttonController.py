from PyQt5.QtCore import QPropertyAnimation

class buttonController:
    def __init__(self, view):
        self.view = view

    def handle_close(self):
        self.view.close()

    def handle_hidden(self):
        self.fade_animation = QPropertyAnimation(self.view, b"windowOpacity")
        self.fade_animation.setDuration(100)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self._minimize)
        self.fade_animation.start()

    def _minimize(self):
        self.view.showMinimized()
        self.view.setWindowOpacity(1.0)

    def toggle_maximize_restore(self):
        if self.view.isMaximized():
            self.view.showNormal()                # Thu nhỏ về kích thước ban đầu
            self.view.maximizeBtn.show()          # Hiện nút maximize
            self.view.restoreBtn.hide()           # Ẩn nút restore
        else:
            self.view.showMaximized()             # Phóng to full màn hình
            self.view.maximizeBtn.hide()          # Ẩn nút maximize
            self.view.restoreBtn.show()           # Hiện nút restore
