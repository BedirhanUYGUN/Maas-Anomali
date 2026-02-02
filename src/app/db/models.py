from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Float, String, Date
from datetime import date

class Base(DeclarativeBase):
    pass

class PayrollRecord(Base):
    __tablename__ = "payroll_records"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    personel_ad: Mapped[str] = mapped_column(String, index=True)
    donem: Mapped[date] = mapped_column(Date, index=True)
    
    # Kazançlar
    maas: Mapped[float] = mapped_column(Float, default=0.0)
    mesai: Mapped[float] = mapped_column(Float, default=0.0)
    mesai_saati: Mapped[float] = mapped_column(Float, default=0.0)
    ek: Mapped[float] = mapped_column(Float, default=0.0)
    yardim: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Kesintiler
    bes: Mapped[float] = mapped_column(Float, default=0.0)
    avans: Mapped[float] = mapped_column(Float, default=0.0)
    icra: Mapped[float] = mapped_column(Float, default=0.0)
    borc: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Ödemeler
    banka: Mapped[float] = mapped_column(Float, default=0.0)
    kasa: Mapped[float] = mapped_column(Float, default=0.0)
    
    @property
    def toplam_kazanc(self) -> float:
        return self.maas + self.mesai + self.ek + self.yardim
    
    @property
    def toplam_kesinti(self) -> float:
        return self.bes + self.avans + self.icra + self.borc

    @property
    def toplam_odeme(self) -> float:
        return self.banka + self.kasa
