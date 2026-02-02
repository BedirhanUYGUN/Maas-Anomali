import sys
import os
import multiprocessing
import traceback

# Version Info
VERSION = "0.2.3"

# Fix for Windowed/Noconsole mode where sys.stdout/stderr are None
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

def log_error(error_msg):
    """Writes error to a file since terminal might be hidden"""
    try:
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{VERSION} - HATA: {error_msg}\n")
            f.write(traceback.format_exc() + "\n" + "-"*30 + "\n")
    except:
        pass

# Critical: Force-import hidden dependencies for PyInstaller
try:
    import aiosqlite
    import sqlalchemy.dialects.sqlite.aiosqlite
except ImportError:
    log_error("Bazı veritabanı sürücüleri yüklenemedi!")

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if getattr(sys, 'frozen', False):
    if hasattr(sys, '_MEIPASS'):
        if sys._MEIPASS not in sys.path:
            sys.path.insert(0, sys._MEIPASS)

try:
    from src.app.main import app
    import uvicorn
except Exception as e:
    log_error(f"Modüller yüklenirken bir sorun oluştu: {e}")
    sys.exit(1)

# Custom uvicorn logging config to avoid 'isatty' check crash in windowed mode
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelprefix)s %(message)s",
            "use_colors": False,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["default"], "level": "INFO"},
    },
}

if __name__ == "__main__":
    # Required for PyInstaller + multiprocessing
    multiprocessing.freeze_support()
    
    try:
        # Run uvicorn with safe logging config
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info", log_config=LOGGING_CONFIG)
    except Exception as e:
        log_error(f"Sunucu başlatılamadı: {e}")
        sys.exit(1)
