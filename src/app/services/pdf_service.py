import pdfplumber
import re
from datetime import datetime
from typing import List, Optional, Tuple
from src.app.db.models import PayrollRecord
import concurrent.futures
import os
import multiprocessing

def clean_currency(value: Optional[str]) -> float:
    if value is None or value == '' or value == '0':
        return 0.0
    cleaned = str(value).replace('.', '').replace(',', '.')
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def extract_period(text: str) -> Optional[datetime]:
    match = re.search(r'(\d{4})\s+(\w+)\s+Dönemi', text)
    if match:
        year = int(match.group(1))
        month_str = match.group(2).lower()
        month_map = {
            'ocak': 1, 'şubat': 2, 'mart': 3, 'nisan': 4,
            'mayıs': 5, 'haziran': 6, 'temmuz': 7, 'ağustos': 8,
            'eylül': 9, 'ekim': 10, 'kasım': 11, 'aralık': 12
        }
        month = month_map.get(month_str, 1)
        return datetime(year, month, 1)
    return None

def process_page_chunk(file_path: str, page_indices: List[int]) -> Tuple[List[dict], Optional[datetime]]:
    """Helper to process a set of pages in a separate process"""
    local_records_data = []
    found_period = None
    
    # Table settings for speed and accuracy
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "join_tolerance": 3,
    }

    try:
        with pdfplumber.open(file_path) as pdf:
            for idx in page_indices:
                page = pdf.pages[idx]
                
                # Only extract period from first encountered text with it
                if not found_period:
                    text = page.extract_text()
                    found_period = extract_period(text)
                
                tables = page.extract_tables(table_settings)
                for table in tables:
                    for row in table:
                        if not row or len(row) < 17:
                            continue
                        
                        if row[0] == 'TOPLAM' or not row[0] or not str(row[0]).isdigit():
                            continue
                        
                        # Store as dict for easier pickling back to main process
                        rec_dict = {
                            "personel_ad": row[1],
                            "maas": clean_currency(row[7]),
                            "mesai": clean_currency(row[8]),
                            "mesai_saati": clean_currency(row[6]),
                            "ek": clean_currency(row[9]),
                            "yardim": clean_currency(row[10]),
                            "bes": clean_currency(row[11]),
                            "avans": clean_currency(row[12]),
                            "icra": clean_currency(row[13]),
                            "borc": clean_currency(row[14]),
                            "banka": clean_currency(row[15]),
                            "kasa": clean_currency(row[16])
                        }
                        local_records_data.append(rec_dict)
    except Exception as e:
        print(f"Error processing pages {page_indices}: {e}")
        
    return local_records_data, found_period

def parse_payroll_pdf(file_path: str) -> List[PayrollRecord]:
    """Parse PDF using multiprocessing for speed"""
    all_records = []
    final_period = None
    
    with pdfplumber.open(file_path) as pdf:
        num_pages = len(pdf.pages)
        if num_pages == 0:
            return []

    # Chunk pages based on CPU count
    cpu_count = min(os.cpu_count() or 1, num_pages)
    chunk_size = (num_pages + cpu_count - 1) // cpu_count
    chunks = [list(range(i, min(i + chunk_size, num_pages))) for i in range(0, num_pages, chunk_size)]

    # Use ProcessPoolExecutor for true parallelism
    with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count) as executor:
        futures = [executor.submit(process_page_chunk, file_path, chunk) for chunk in chunks]
        
        for future in concurrent.futures.as_completed(futures):
            recs_data, period = future.result()
            if period and not final_period:
                final_period = period
            
            # Convert dicts back to PayrollRecord objects
            for data in recs_data:
                record = PayrollRecord(
                    personel_ad=data["personel_ad"],
                    donem=final_period.date() if final_period else datetime.now().date(),
                    maas=data["maas"],
                    mesai=data["mesai"],
                    mesai_saati=data["mesai_saati"],
                    ek=data["ek"],
                    yardim=data["yardim"],
                    bes=data["bes"],
                    avans=data["avans"],
                    icra=data["icra"],
                    borc=data["borc"],
                    banka=data["banka"],
                    kasa=data["kasa"]
                )
                all_records.append(record)

    # Correct the period for all records if it was found late
    if final_period:
        for r in all_records:
            r.donem = final_period.date()

    return all_records
