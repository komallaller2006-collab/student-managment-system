import config
from database import studentmanagementsystem
from gui import MainWindow
from login import LoginWindow


def main() -> None:
    sms = studentmanagementsystem(config.DATABASE_PATH)

    def launch_main_app(username: str) -> None:
        app = MainWindow(sms, username)
        app.mainloop()

    login_window = LoginWindow(sms, on_success=launch_main_app)
    login_window.mainloop()


if __name__ == '__main__':
    main()
    