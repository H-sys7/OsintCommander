import logging
import sys
from datetime import datetime
import os
from src.core.paths import get_app_temp_dir

LOG_DIR = os.path.join(get_app_temp_dir(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logger(name="OsintLogger"):
    """
    Configure un logger qui écrit dans la console et dans un fichier daté.
    Pour la GUI, on pourra ajouter un Handler spécifique plus tard.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Éviter les doublons si on appelle la fonction plusieurs fois
    if logger.handlers:
        return logger

    # Formattage des messages
    # Ex: [2023-10-27 14:00:00] [INFO] - Message
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # 1. Handler Fichier (garde une trace de tout)
    log_filename = f"{LOG_DIR}/session_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 2. Handler Console (pour voir les erreurs dans ton IDE pendant le dev)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Instance globale
logger = setup_logger()