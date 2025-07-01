from src.views.login_view import LoginWindow
from src.views.main_view import MainWindow
from src.views.addChar_view import AddCharWindow
from src.controllers.LoginController import LoginController
from src.views.student.student_form_view import StudentForm

def open_login_window():
    window = LoginWindow()
    controller = LoginController(window)
    window.controller = controller
    window.show()
    return window

def open_main_window(username):
    window = MainWindow(username)
    window.show()
    return window

def open_addChar_window():
    window = AddCharWindow()
    window.show()
    return window

