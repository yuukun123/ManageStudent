from src.views.login_view import LoginWindow
from src.views.dashboard_view import DashboardWindow
from src.controllers.LoginController import LoginController

def open_login_window():
    window = LoginWindow()
    controller = LoginController(window)
    window.controller = controller
    window.show()
    return window

def open_dashboard_window(username):
    window = DashboardWindow(username)
    window.show()
    return window
