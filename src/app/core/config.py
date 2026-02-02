from pydantic_settings import BaseSettings
import os
import sys

class Settings(BaseSettings):
    PROJECT_NAME: str = "Maaş-Mesai Tespit"
    VERSION: str = "0.2.0"
    API_V1_STR: str = "/api/v1"
    
    @property
    def BASE_DIR(self) -> str:
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.getcwd()

    @property
    def DATABASE_URL(self) -> str:
        db_path = os.path.join(self.BASE_DIR, "data.db")
        return f"sqlite+aiosqlite:///{db_path}"

settings = Settings()
