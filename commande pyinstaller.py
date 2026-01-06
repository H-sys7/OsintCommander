pyinstaller ^
 --onefile ^
 --windowed ^
 --name OsintCommander ^
 --collect-all customtkinter ^
 --collect-all tkinter ^
 --collect-all pkg_resources ^
 --hidden-import src ^
 --hidden-import src.collectors ^
 --hidden-import src.processors ^
 --hidden-import src.core ^
 --hidden-import src.ai ^
 main.py
