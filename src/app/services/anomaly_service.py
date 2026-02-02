from typing import List, Dict, Any, Tuple
from src.app.db.models import PayrollRecord
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date, timedelta

class AnomalyService:
    @staticmethod
    def check_rule_1(record: PayrollRecord) -> Tuple[bool, float]:
        """Kazanç = Kesinti + Ödeme (Denklik Kontrolü)"""
        kazanc = record.maas + record.mesai + record.ek + record.yardim
        kesinti = record.bes + record.avans + record.icra + record.borc
        odeme = record.banka + record.kasa
        
        diff = kazanc - (kesinti + odeme)
        return abs(diff) <= 10.0, diff

    @staticmethod
    async def check_rule_2(db: AsyncSession, record: PayrollRecord) -> Tuple[bool, Dict[str, Any]]:
        """%20'den fazla ücret artışı kontrolü"""
        prev_month_date = record.donem - timedelta(days=5)
        prev_month_date = prev_month_date.replace(day=1)
        
        query = select(PayrollRecord).where(
            and_(
                PayrollRecord.personel_ad == record.personel_ad,
                PayrollRecord.donem == prev_month_date
            )
        )
        result = await db.execute(query)
        prev_record = result.scalars().first()
        
        current_total = record.maas + record.mesai + record.ek + record.yardim
        
        if prev_record:
            prev_total = prev_record.maas + prev_record.mesai + prev_record.ek + prev_record.yardim
            if prev_total > 0:
                increase = (current_total - prev_total) / prev_total
                if increase > 0.20:
                    return False, {
                        "prev_total": prev_total,
                        "current_total": current_total,
                        "increase_pct": increase * 100
                    }
        return True, {}

    @staticmethod
    def check_rule_3(record: PayrollRecord) -> bool:
        """48 saatten fazla mesai kontrolü"""
        return record.mesai_saati <= 48.0

    @classmethod
    async def get_anomalies(cls, db: AsyncSession, records: List[PayrollRecord]) -> List[Dict[str, Any]]:
        anomalies = []
        for rec in records:
            issues = []
            categories = set()
            rule_details = {}
            
            # Maaş Dengesi (Eski Kural 1)
            is_valid_r1, diff = cls.check_rule_1(rec)
            if not is_valid_r1:
                issues.append(f"Maaş sorunu: Ödeme dengesizliği (Fark: {diff:.2f} TL)")
                categories.add("maaş")
            
            # Maaş Artışı (Eski Kural 2)
            is_valid_r2, r2_data = await cls.check_rule_2(db, rec)
            if not is_valid_r2:
                issues.append(f"Maaş sorunu: %{r2_data['increase_pct']:.1f} yüksek artış tespit edildi.")
                categories.add("maaş")
                rule_details["salary_increase"] = r2_data
            
            # Mesai Sınırı (Eski Kural 3)
            if not cls.check_rule_3(rec):
                issues.append(f"Mesai sorunu: Aylık mesai sınırı aşıldı ({rec.mesai_saati} saat)")
                categories.add("mesai")
            
            if issues:
                anomalies.append({
                    "personel_ad": rec.personel_ad,
                    "donem": rec.donem.strftime("%Y-%m"),
                    "maas": rec.maas,
                    "mesai": rec.mesai,
                    "mesai_saati": rec.mesai_saati,
                    "ek": rec.ek,
                    "yardim": rec.yardim,
                    "bes": rec.bes,
                    "avans": rec.avans,
                    "icra": rec.icra,
                    "borc": rec.borc,
                    "banka": rec.banka,
                    "kasa": rec.kasa,
                    "issues": issues,
                    "details": rule_details,
                    "categories": list(categories)
                })
        return anomalies
