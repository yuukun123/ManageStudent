class LogoutController:
    def __init__(self, view):
        self.view = view

    def handle_logout(self):
        from src.windows.window_manager import open_login_window
        open_login_window()
        self.view.close()
