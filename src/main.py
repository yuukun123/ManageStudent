import sys
from PyQt5 import QtWidgets
from src.views.login_view import LoginWindow
from src.controllers.LoginController import LoginController
from src.models.user_model import get_all_users


if __name__ == "__main__":
    # app = QtWidgets.QApplication(sys.argv)
    # MainWindow = LoginWindow()
    # # ui = Ui_MainWindow()
    # # ui.setupUi(MainWindow)
    # MainWindow.show()
    # sys.exit(app.exec_())

    app = QtWidgets.QApplication([])
    window = LoginWindow()
    # Gắn controller login
    login_controller = LoginController(window.ui)
    window.show()
    app.exec_()

    users = get_all_users()
    for user in users:
        print(f"ID: {user[0]}, Username: {user[1]}")