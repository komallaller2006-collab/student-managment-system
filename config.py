import os
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR=os.path.join(BASE_DIR,"database")
DB_PATH=os.path.join(DATABASE_DIR,"student_management.db")
DATABASE_PATH=DB_PATH
ASSETS_DIR=os.path.join(BASE_DIR,"assets")
ICON_DIR=os.path.join(ASSETS_DIR,"icons")
LOGO_DIR=os.path.join(ASSETS_DIR,"logo")
icons={
        "add":os.path.join(ICON_DIR,"add.png"),
        "delete":os.path.join(ICON_DIR,"delete.png"),
        "edit":os.path.join(ICON_DIR,"edit.png"),
        "search":os.path.join(ICON_DIR,"search.png"),
        "refresh":os.path.join(ICON_DIR,"refresh.png"),
        "export":os.path.join(ICON_DIR,"export.png"),
        "stats":os.path.join(ICON_DIR,"stats.png"),
        "logo":os.path.join(LOGO_DIR,"logo.png"),
        "grade":os.path.join(ICON_DIR,"grade.png"),
        "logout":os.path.join(ICON_DIR,"logout.png"),
        "user":os.path.join(ICON_DIR,"user.png"),
}
ICON=icons
LOGO_PATH=icons.get("logo")
APP_NAME="Student Management System"
APP_VERSION="1.0"
LOGIN_WINDOW_TITLE="Login - Student Management System"
LOGIN_WINDOW_SIZE="400x300"
MAIN_WINDOW_SIZE="900x600"
DEFAULT_FONT=("Arial", 12)
DEFAULT_BG_COLOR="#f0f0f0"
DEFAULT_FG_COLOR="#000000"
DEFAULT_ADMIN_USERNAME="admin"
DEFAULT_ADMIN_PASSWORD="admin123"
MAX_LOGIN_ATTEMPTS=5
COLORS={
    "primary": "#2563eb",
    "secondary": "#64748b",
    "primary_dark": "#1e40af",
    "success": "#4CAF50",
    "danger": "#F44336",
    "warning": "#FF9800",
    "border" : "#cbd5e1",
    "text" : "#212529",
    "background" : "#ffffff",
    "row_even" : "#f8f9fa",
    "header" : "#1e293b",
    "row_odd" : "#f8fafc",
    "text_muted":"#64748b",
    "surface":"#ffffff"
}
FONTS={
    "header": ("segoe ui", 14, "bold"),
    "subheader": ("segoe ui", 12, "bold"),
    "body": ("segoe ui", 12),
    "body_bold": ("segoe ui", 12, "bold"),
    "small": ("segoe ui", 10),
    "monospaced": ("Courier New", 12),
}
GRADE_LEVELS=[
    "KINDERGARTEN",
    "GRADE_1",
    "GRADE_2",
    "GRADE_3",
    "GRADE_4",
    "GRADE_5",
    "GRADE_6",
    "GRADE_7",
    "GRADE_8",
    "GRADE_9",
    "GRADE_10",
    "GRADE_11",
    "GRADE_12",
    "UNDERGRADUATE",
    "POSTGRADUATE"
]
