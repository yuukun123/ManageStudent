from PyQt5 import uic
from PyQt5.QtCore import Qt
from src.controllers.buttonController import buttonController
from src.views.moveable_window import MoveableWindow
from resources import resources_rc

class AddCharWindow(MoveableWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("../UI/forms/addChar.ui", self)
        self.invisible()
        # Tạo controller, truyền self vào
        self.buttonController = buttonController(self)
        # Gán nút
        self.cancelBtn.clicked.connect(self.buttonController.handle_cancel)





