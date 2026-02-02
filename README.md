# Maaş-Mesai Tespit Sistemi

Bu uygulama, personel maaş bordrolarını (PDF) analiz ederek maaş dengesizliklerini ve aşırı mesai durumlarını otomatik olarak tespit eder. Tamamen taşınabilir (Single EXE) mimarisi sayesinde kurulum gerektirmeden her bilgisayarda çalışabilir.

## ✨ Özellikler

- **PDF Veri Çıkarma**: Birden fazla bordro dosyasından otomatik veri çekme.
- **Anomali Tespit Kuralları**:
  - **Denge Kontrolü**: Hakedişlerin ödemelerle eşleşip eşleşmediğini denetler.
  - **Maaş Karşılaştırma**: Bir önceki aya göre %20'den fazla artışları raporlar.
  - **Mesai Takibi**: Aylık 48 saati aşan aşırı mesaileri tespit eder.
- **Yerel Dosya Desteği**: Uygulamanın yanındaki PDF'leri otomatik algılar ve listeler.
- **Penceresiz Çalışma**: Siyah CMD ekranı olmadan, modern web arayüzü ile doğrudan etkileşim.
- **Otomatik Temizleme**: Her yeni açılışta veritabanını sıfırlayarak "temiz sayfa" sunar.

## 📥 İndirme

| İşletim Sistemi | İşlem |
| :--- | :--- |
| **Windows 10/11** | [� **İndir (v0.2.3 EXE)**](https://github.com/BedirhanUYGUN/Maas-Anomali/releases/latest) |

## 🚀 Çalıştırma

1. `dist/MaasAnomali.exe` dosyasını bilgisayarınızın herhangi bir yerine kopyalayın.
2. Analiz etmek istediğiniz PDF dosyalarını bu `.exe` dosyasının yanına koyun.
3. Uygulamayı çalıştırın. Birkaç saniye içinde tarayıcınız (Chrome/Edge) sistem arayüzü ile açılacaktır.

## 🛠️ Teknik Detaylar

- **Backend**: FastAPI (Python)
- **Frontend**: React (Vite)
- **Paketleme**: PyInstaller (Single File, Windowed)
- **Veritabanı**: SQLite (Geçici oturum bazlı)

---
*Geliştirici: Antigravity*
