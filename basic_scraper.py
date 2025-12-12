# scrapers/basic_scraper.py

import time
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, HTTPError

# Telif notu: app.py dosyasındaki telif hakkı ve lisans bilgilerine bakınız.

# İYİLEŞTİRME 1: Gelişmiş User-Agent (Bot Algılanmasını Önlemek İçin)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Connection': 'keep-alive'
}

def perform_scrape(url, selectors, delay):
    """
    Belirtilen URL'den veriyi çeker, CSS seçicileri uygular ve sonuçları döndürür.
    
    Args:
        url (str): Kazınacak URL.
        selectors (list): Aranacak CSS seçicilerin listesi.
        delay (int): Her istek arasında uygulanacak etik gecikme süresi (saniye).
        
    Returns:
        tuple: (list - Kazınan veriler, int - HTTP Durum Kodu, str - Hata mesajı veya boş)
    """
    time.sleep(delay)  # Etik gecikme
    
    scraped_data = []
    status_code = 0
    error_message = "" # Yeni eklendi: Hata mesajını taşımak için
    
    try:
        # HTTP isteği gönder (HEADERS eklendi)
        response = requests.get(url, timeout=10, headers=HEADERS) 
        status_code = response.status_code
        response.raise_for_status() # 4xx veya 5xx durum kodlarında istisna fırlat
        
        # HTML içeriğini ayrıştır
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Her bir seçici için veriyi topla
        for selector in selectors:
            elements = soup.select(selector)
            
            # Bulunan her elementin metin içeriğini kaydet
            for element in elements:
                text = element.get_text(strip=True)
                
                # Çıktı formatını oluştur
                scraped_data.append({
                    "selector": selector,
                    "data": text
                })
                
        return scraped_data, status_code, error_message
        
    # İYİLEŞTİRME 2 ve 3: Hata yakalama blokları birleştirildi ve üst katmana mesaj dönüldü.
    except HTTPError as e:
        error_message = f"HTTP Hatası ({status_code}): Erişim reddedildi, sayfa bulunamadı veya sunucu hatası."
        print(f"Hata oluştu: {e}")
        return scraped_data, status_code, error_message
    
    except RequestException as e:
        # Ağ hataları, timeout, DNS sorunları gibi genel Request hataları
        status_code = status_code if status_code != 0 else 500
        error_message = f"Bağlantı Hatası ({status_code}): İstek zaman aşımına uğradı veya ağ sorunu var."
        print(f"Hata oluştu: {e}")
        return scraped_data, status_code, error_message
    
    except Exception as e:
        # Diğer beklenmedik hatalar (Ayrıştırma, vs.)
        error_message = f"Beklenmedik Genel Hata: {str(e)}"
        print(f"Genel hata: {e}")
        return scraped_data, 500, error_message