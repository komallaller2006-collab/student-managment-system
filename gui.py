import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import config
from database import studentmanagementsystem, ValidationError, DatabaseError
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def load_icon(name, size=(18, 18)):
    if not PIL_AVAILABLE:
        return None
    try:
        img = Image.open(config.ICON[name]).resize(size)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


class StudentDialog(tk.Toplevel):
    def __init__(self, parent, sms: studentmanagementsystem, student=None, on_saved=None):
        super().__init__(parent)
        self.sms = sms
        self.student = student
        self.on_saved = on_saved
        self.title('Edit Student' if student else 'Add Student')
        self.geometry('500x380')
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self._build_ui()
        if student is not None:
            self._populate_from_student()

    def _build_ui(self):
        pad = 8
        frame = ttk.Frame(self, padding=pad)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text='Name:').grid(row=0, column=0, sticky=tk.W, pady=pad)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(frame, textvariable=self.name_var, width=40)
        self.name_entry.grid(row=0, column=1, sticky=tk.W, pady=pad)

        ttk.Label(frame, text='Age:').grid(row=1, column=0, sticky=tk.W, pady=pad)
        self.age_var = tk.StringVar()
        self.age_entry = ttk.Entry(frame, textvariable=self.age_var, width=15)
        self.age_entry.grid(row=1, column=1, sticky=tk.W, pady=pad)

        ttk.Label(frame, text='Grade:').grid(row=2, column=0, sticky=tk.W, pady=pad)
        self.grade_var = tk.StringVar()
        self.grade_entry = ttk.Entry(frame, textvariable=self.grade_var, width=30)
        self.grade_entry.grid(row=2, column=1, sticky=tk.W, pady=pad)

        ttk.Label(frame, text='Photo:').grid(row=3, column=0, sticky=tk.W, pady=pad)
        self.photo_var = tk.StringVar()
        photo_frame = ttk.Frame(frame)
        photo_frame.grid(row=3, column=1, sticky=tk.W, pady=pad)
        self.photo_entry = ttk.Entry(photo_frame, textvariable=self.photo_var, width=30)
        self.photo_entry.pack(side=tk.LEFT)
        browse_btn = ttk.Button(photo_frame, text='Browse...', command=self._on_browse_photo)
        browse_btn.pack(side=tk.LEFT, padx=(6, 0))

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        save_btn = ttk.Button(btn_frame, text='Save', command=self._on_save)
        save_btn.pack(side=tk.LEFT, padx=6)
        cancel_btn = ttk.Button(btn_frame, text='Cancel', command=self.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=6)

        self.name_entry.focus_set()

    def _populate_from_student(self):
        student = self.student
        if student is None:
            return

        if isinstance(student, dict):
            self.name_var.set(student.get('name', ''))
            self.age_var.set(str(student.get('age', '')) if student.get('age') is not None else '')
            self.grade_var.set(student.get('grade', ''))
            self.photo_var.set(student.get('photo', ''))
        else:
            self.name_var.set(getattr(student, 'name', ''))
            age = getattr(student, 'age', None)
            self.age_var.set(str(age) if age is not None else '')
            self.grade_var.set(getattr(student, 'grade', ''))
            self.photo_var.set(getattr(student, 'photo', ''))

    def _on_browse_photo(self):
        path = filedialog.askopenfilename(
            title='Select photo',
            filetypes=[('Image files', '*.png;*.jpg;*.jpeg;*.gif'), ('All files', '*.*')],
        )
        if path:
            self.photo_var.set(path)

    def _on_save(self):
        data = {
            'name': self.name_var.get().strip(),
            'age': self.age_var.get().strip(),
            'grade': self.grade_var.get().strip(),
            'photo': self.photo_var.get().strip(),
        }
        if not data['name']:
            messagebox.showerror('Validation error', 'Name is required')
            return

        try:
            if data['age']:
                data['age'] = int(data['age'])
            else:
                data['age'] = None
        except ValueError:
            messagebox.showerror('Validation error', 'Age must be a number')
            return

        try:
            if self.student is not None and getattr(self.student, 'id', None):
                self.sms.update_student(self.student.id, data)
            else:
                self.sms.create_student(data)
        except ValidationError as ve:
            messagebox.showerror('Validation error', str(ve))
            return
        except DatabaseError as de:
            messagebox.showerror('Database error', str(de))
            return
        except Exception as e:
            messagebox.showerror('Error', str(e))
            return

        if callable(self.on_saved):
            try:
                self.on_saved()
            except Exception:
                pass
        self.destroy()


class MainWindow(tk.Tk):
    def __init__(self, sms: studentmanagementsystem, username: str):
        super().__init__()
        self.sms = sms
        self.username = username
        self.title(config.APP_NAME)
        self.geometry(config.MAIN_WINDOW_SIZE)
        self.configure(bg=config.DEFAULT_BG_COLOR)
        self._build_ui()
        self._load_students()

    def _build_ui(self):
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill=tk.X)

        title_label = ttk.Label(top_frame, text=f'Welcome, {self.username}', font=config.FONTS['header'])
        title_label.pack(side=tk.LEFT)

        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.RIGHT)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=24)
        search_entry.pack(side=tk.LEFT, padx=(0, 6))
        search_entry.bind('<Return>', lambda event: self._load_students())

        search_btn = ttk.Button(search_frame, text='Search', command=self._load_students)
        search_btn.pack(side=tk.LEFT, padx=(0, 6))

        refresh_btn = ttk.Button(search_frame, text='Refresh', command=self._load_students)
        refresh_btn.pack(side=tk.LEFT)

        content_frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        content_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('id', 'name', 'age', 'grade', 'photo')
        self.tree = ttk.Treeview(content_frame, columns=columns, show='headings', selectmode='browse')
        self.tree.heading('name', text='Name')
        self.tree.heading('age', text='Age')
        self.tree.heading('grade', text='Grade')
        self.tree.heading('photo', text='Photo')
        self.tree.column('id', width=0, stretch=False)
        self.tree.column('name', width=260)
        self.tree.column('age', width=70, anchor=tk.CENTER)
        self.tree.column('grade', width=120)
        self.tree.column('photo', width=320)

        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        content_frame.rowconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=1)

        button_frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        button_frame.pack(fill=tk.X)

        add_btn = ttk.Button(button_frame, text='Add Student', command=self._on_add)
        add_btn.pack(side=tk.LEFT)
        edit_btn = ttk.Button(button_frame, text='Edit Student', command=self._on_edit)
        edit_btn.pack(side=tk.LEFT, padx=6)
        delete_btn = ttk.Button(button_frame, text='Delete Student', command=self._on_delete)
        delete_btn.pack(side=tk.LEFT)

    def _load_students(self):
        query = self.search_var.get().strip()
        try:
            students = self.sms.get_students(query if query else None)
        except Exception as e:
            messagebox.showerror('Error loading students', str(e))
            return

        self.tree.delete(*self.tree.get_children())
        for student in students:
            self.tree.insert('', tk.END, values=(student.id, student.name, student.age or '', student.grade, student.photo))

    def _get_selected_student_id(self):
        selection = self.tree.selection()
        if not selection:
            return None
        item = self.tree.item(selection[0])
        return int(item['values'][0]) if item['values'] else None

    def _on_add(self):
        StudentDialog(self, self.sms, on_saved=self._load_students)

    def _on_edit(self):
        student_id = self._get_selected_student_id()
        if student_id is None:
            messagebox.showwarning('Select student', 'Please select a student to edit.')
            return
        try:
            student = self.sms.get_student(student_id)
        except Exception as e:
            messagebox.showerror('Error', str(e))
            return
        StudentDialog(self, self.sms, student=student, on_saved=self._load_students)

    def _on_delete(self):
        student_id = self._get_selected_student_id()
        if student_id is None:
            messagebox.showwarning('Select student', 'Please select a student to delete.')
            return
        if not messagebox.askyesno('Delete student', 'Are you sure you want to delete the selected student?'):
            return
        try:
            self.sms.delete_student(student_id)
            self._load_students()
        except Exception as e:
            messagebox.showerror('Error deleting student', str(e))
