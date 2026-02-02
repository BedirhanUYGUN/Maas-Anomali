from pydantic import BaseModel
from datetime import date
from typing import List, Optional, Dict, Any

class PayrollRecordBase(BaseModel):
    personel_ad: str
    donem: date
    maas: float
    mesai: float
    mesai_saati: float
    ek: float
    yardim: float
    bes: float
    avans: float
    icra: float
    borc: float
    banka: float
    kasa: float

class PayrollRecordCreate(PayrollRecordBase):
    pass

class PayrollRecordResponse(PayrollRecordBase):
    id: int
    toplam_kazanc: float
    toplam_kesinti: float
    toplam_odeme: float

    class Config:
        from_attributes = True

class AnomalyResponse(BaseModel):
    personel_ad: str
    donem: str
    maas: float
    mesai: float
    mesai_saati: float
    ek: float
    yardim: float
    bes: float
    avans: float
    icra: float
    borc: float
    banka: float
    kasa: float
    issues: List[str]
    diff: Optional[float] = None
    categories: List[str]
    details: Optional[Dict[str, Any]] = None
