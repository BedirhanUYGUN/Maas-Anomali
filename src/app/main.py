from fastapi import FastAPI
from src.app.api.router import api_router
from src.app.core.config import settings
from src.app.db.models import Base
from src.app.db.session import engine, SessionLocal
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
import webbrowser

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

def get_static_path():
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, "frontend", "dist")
    
    base_path = os.getcwd()
    return os.path.join(base_path, "frontend", "dist")

static_path = get_static_path()

app.include_router(api_router, prefix=settings.API_V1_STR)

if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

@app.on_event("startup")
async def startup():
    from sqlalchemy import delete
    from src.app.db.models import PayrollRecord
    
    print("Veritabanı kontrol ediliyor...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Yeni oturum için veriler temizleniyor...")
    async with SessionLocal() as db:
        await db.execute(delete(PayrollRecord))
        await db.commit()
    print("Veritabanı hazır ve boş.")
    
    # Auto open browser in local frozen mode
    if getattr(sys, 'frozen', False) and not os.getenv("DEBUG"):
        url = "http://127.0.0.1:8000"
        print(f"Uygulama başlatıldı! Tarayıcı açılıyor: {url}")
        print("Not: Tarayıcı otomatik açılmazsa yukarıdaki adresi kopyalayıp tarayıcınıza yapıştırın.")
        webbrowser.open(url)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
