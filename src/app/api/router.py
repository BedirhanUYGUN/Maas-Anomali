from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.db.session import get_db
from src.app.services.pdf_service import parse_payroll_pdf
from src.app.services.anomaly_service import AnomalyService
from src.app.db.models import PayrollRecord
from typing import List
import shutil
import os
import tempfile

api_router = APIRouter()

@api_router.post("/upload")
async def upload_payroll(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    # Save temp file
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        records = parse_payroll_pdf(file_path)
        if not records:
             raise HTTPException(status_code=400, detail="PDF'den veri okunamadı veya format geçersiz.")
        
        # Get anomalies for these new records BEFORE commit
        anomalies = await AnomalyService.get_anomalies(db, records)
        
        # Save to DB
        db.add_all(records)
        await db.commit()
        
        return {
            "message": f"{len(records)} kayıt başarıyla işlendi.",
            "anomalies": anomalies
        }
    finally:
        shutil.rmtree(temp_dir)

@api_router.get("/files")
async def list_local_files():
    from src.app.core.config import settings
    base_dir = settings.BASE_DIR
    files = [f for f in os.listdir(base_dir) if f.lower().endswith(".pdf")]
    return {"files": files, "base_dir": base_dir}

@api_router.post("/analyze-local")
async def analyze_local_file(filename: str, db: AsyncSession = Depends(get_db)):
    from src.app.core.config import settings
    file_path = os.path.join(settings.BASE_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dosya bulunamadı.")
    
    records = parse_payroll_pdf(file_path)
    if not records:
         raise HTTPException(status_code=400, detail="PDF'den veri okunamadı.")
    
    anomalies = await AnomalyService.get_anomalies(db, records)
    db.add_all(records)
    await db.commit()
    
    return {
        "message": f"{len(records)} kayıt başarıyla işlendi.",
        "anomalies": anomalies
    }

@api_router.get("/anomalies")
async def get_all_anomalies(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(PayrollRecord))
    all_records = result.scalars().all()
    anomalies = await AnomalyService.get_anomalies(db, all_records)
    return anomalies

@api_router.delete("/clear")
async def clear_data(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import delete
    await db.execute(delete(PayrollRecord))
    await db.commit()
    return {"message": "Tüm veriler başarıyla silindi."}

@api_router.get("/records")
async def get_records(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(PayrollRecord))
    return result.scalars().all()
