# utils/data_handler.py (NİHAİ DÜZELTME - Tablo Adı ve init_db Kaldırıldı)

import sqlite3
import csv
import json
from io import StringIO
from datetime import datetime

DATABASE_NAME = 'database.db'

def init_db():
    """Veritabanını ve gerekli tabloları oluşturur."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # Tarihçe tablosu oluşturuluyor
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scrape_history (  
            id INTEGER PRIMARY KEY,
            url TEXT NOT NULL,
            status_code INTEGER,
            timestamp TEXT NOT NULL,
            data_count INTEGER,
            success BOOLEAN,
            error_msg TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_scrape_to_db(url, status_code, data_count, success, error_msg=""):
    """Kazıma işleminin sonucunu veritabanına kaydeder."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO scrape_history (url, status_code, timestamp, data_count, success, error_msg) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (url, status_code, timestamp, data_count, success, error_msg))
    
    conn.commit()
    conn.close()

def get_history():
    """Veritabanından tüm kazıma geçmişini çeker (En sonuncudan başlayarak)."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # Sütun isimleri ve verileri bir arada getirmek için
    cursor.execute('SELECT * FROM scrape_history ORDER BY timestamp DESC') 
    
    # Sütun isimlerini al
    column_names = [description[0] for description in cursor.description]
    
    # Veri çekme ve sözlük formatına dönüştürme
    history_data = []
    for row in cursor.fetchall():
        history_data.append(dict(zip(column_names, row)))
        
    conn.close()
    return history_data

def convert_to_csv(data):
    """Kazınan listeyi CSV formatında bir dizeye (string) dönüştürür."""
    if not data:
        return ""
    
    # Bellekteki geçici bir dosya gibi davranır
    output = StringIO()
    fieldnames = data[0].keys()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(data)
    
    return output.getvalue()

def convert_to_json(data):
    """Kazınan listeyi JSON formatında bir dizeye dönüştürür."""
    return json.dumps(data, indent=4, ensure_ascii=False)


# init_db() çağrısı buradan kaldırıldı ve app.py'ye taşındı.