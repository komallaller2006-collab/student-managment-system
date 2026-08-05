import tkinter as tk
from tkinter import messagebox
from database import studentmanagementsystem
import config
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class LoginWindow(tk.Tk):
    def __init__(self, sms: studentmanagementsystem, on_success):
        super().__init__()
        self.sms = sms
        self.on_success = on_success
        self.title(config.LOGIN_WINDOW_TITLE)
        self.geometry(config.LOGIN_WINDOW_SIZE)
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        if PIL_AVAILABLE and config.LOGO_PATH:
            try:
                image = Image.open(config.LOGO_PATH)
                image = image.resize((100, 100), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(image)
                logo_label = tk.Label(self, image=photo)
                logo_label.image = photo
                logo_label.pack(pady=10)
            except Exception as e:
                print(f'Error loading logo: {e}')

        username_label = tk.Label(self, text='Username:')
        username_label.pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        password_label = tk.Label(self, text='Password:')
        password_label.pack(pady=5)
        self.password_entry = tk.Entry(self, show='*')
        self.password_entry.pack(pady=5)

        login_button = tk.Button(self, text='Login', command=self.login)
        login_button.pack(pady=20)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror('Login Failed', 'Enter both username and password.')
            return

        if self.sms.authenticate_user(username, password):
            messagebox.showinfo('Login Successful', f'Welcome {username}!')
            self.destroy()
            self.on_success(username)
        else:
            messagebox.showerror('Login Failed', 'Invalid username or password.')

