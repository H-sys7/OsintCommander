import os
import tempfile

def get_app_temp_dir():
    base = os.getenv("APPDATA")
    if base is None:
        raise EnvironmentError("APPDATA environment variable is not set.")
    temp_dir = os.path.join(base, "OsintCommander", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir