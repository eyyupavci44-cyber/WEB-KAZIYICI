# scrapers/advanced_scraper.py

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

# Telif notu: app.py dosyasındaki telif hakkı ve lisans bilgilerine bakınız.

def perform_advanced_scrape(url, selectors, delay):
    """
    JavaScript ile yüklenen dinamik içerikleri Selenium kullanarak çeker.
    
    Args:
        url (str): Kazınacak URL.
        selectors (list): Aranacak CSS seçicilerin listesi.
        delay (int): Tarayıcı başlatıldıktan ve sayfa yüklendikten sonraki bekleme süresi (saniye).
        
    Returns:
        tuple: (list - Kazınan veriler, int - Durum Kodu, str - Hata mesajı)
    """
    
    scraped_data = []
    status_code = 200 
    error_message = ""
    
    # 1. Tarayıcı Seçeneklerini Ayarlama (Headless Mod)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Görsel arayüzü gizle
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    # Gelişmiş User-Agent ekleme (Bot algılanmasını azaltır)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    
    driver = None
    try:
        # Tarayıcıyı başlat
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30) # Sayfa yükleme süresi sınırı
        
        time.sleep(delay) # Etik Gecikme (Tarayıcı başlatıldıktan sonra)
        
        # URL'ye git
        driver.get(url)
        
        # Dinamik içeriğin yüklenmesi için ek bekleme (delay süresi kadar)
        time.sleep(delay) 
        
        # 2. Veriyi Çekme
        for selector in selectors:
            try:
                # Selenium'da By.CSS_SELECTOR kullanılır
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    text = element.text.strip()
                    if text: 
                         scraped_data.append({
                            "selector": selector,
                            "data": text
                        })
            except Exception:
                # Seçici bulunamazsa sessizce geç
                pass
        
        status_code = 200 
        
    except TimeoutException:
        status_code = 408
        error_message = "Zaman Aşımı Hatası: Sayfa 30 saniye içinde yüklenemedi."
    except WebDriverException as e:
        status_code = 500
        error_message = f"Sürücü Hatası: Tarayıcı sürücüsü bulunamadı veya başlatılamadı. Lütfen kontrol edin. Hata: {e}"
    except Exception as e:
        status_code = 500
        error_message = f"Beklenmedik Genel Hata: {str(e)}"
    finally:
        if driver:
            driver.quit() # Tarayıcıyı mutlaka kapat
            
    return scraped_data, status_code, error_message