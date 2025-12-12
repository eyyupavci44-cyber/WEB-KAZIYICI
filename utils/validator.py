# utils/validator.py

import requests
from urllib.parse import urljoin, urlparse
from requests.exceptions import RequestException

# Telif notu: app.py dosyasındaki telif hakkı ve lisans bilgilerine bakınız.

# robots.txt dosyasını kontrol etmek için kullanılan varsayılan User-Agent
# Kendi bot isminizi kullanmanız daha şeffaf ve profesyoneldir.
# Örn: 'MyScraperBot/1.0'
DEFAULT_BOT_NAME = "WebScraperProject" 

def check_robots_txt(url):
    """
    Verilen URL için sitenin robots.txt dosyasını kontrol eder.
    Kazıma yapılmasına izin verilip verilmediğini döndürür.
    
    Args:
        url (str): Kazınacak sayfanın URL'si.
        
    Returns:
        tuple: (bool - İzin verildi mi?, str - Hata veya Durum mesajı)
    """
    
    # 1. robots.txt URL'sini oluştur
    parsed_url = urlparse(url)
    # Temel URL: https://example.com/yazi/1 -> https://example.com/
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    robots_url = urljoin(base_url, '/robots.txt')
    
    # 2. robots.txt dosyasını çek
    try:
        response = requests.get(robots_url, timeout=5)
        
        # 3. robots.txt dosyası yoksa veya erişilemiyorsa (404/403), genellikle izin verildi varsayılır.
        if response.status_code >= 400:
            return True, f"robots.txt bulunamadı (HTTP {response.status_code}). Devam ediliyor."

        # 4. İçeriği kontrol et (Basit kontrol)
        content = response.text
        
        # Sitenin tüm botları yasaklayıp yasaklamadığını kontrol et (Disallow: /)
        if "User-agent: *" in content and "Disallow: /" in content:
             return False, "Hata: robots.txt, tüm botlar için siteyi tamamen yasaklamıştır (Disallow: /)."
        
        # Kendi User-Agent'ımız için özel bir yasaklama olup olmadığını kontrol et
        if f"User-agent: {DEFAULT_BOT_NAME}" in content:
            # Botumuzun yasaklanmış path'lerini bulmak için gelişmiş ayrıştırıcı kullanılabilir.
            # Şimdilik basitleştirilmiş kontrol yapıyoruz:
            if "Disallow: /" in content.split(f"User-agent: {DEFAULT_BOT_NAME}")[1]:
                 return False, f"Hata: robots.txt, özel botunuz '{DEFAULT_BOT_NAME}' için siteyi yasaklamıştır."

        # Daha gelişmiş bir kontrol için 'robotparser' kullanılabilir, ancak basit bir kontrolle devam ediyoruz.
        return True, "robots.txt kontrol edildi. Kazıma işlemine etik olarak izin verildi."
        
    except RequestException:
        # Ağ hatası veya timeout durumunda
        return True, "Uyarı: robots.txt kontrolü başarısız oldu (Ağ hatası). Devam ediliyor."
    
    except Exception as e:
        return True, f"Uyarı: robots.txt kontrolü sırasında beklenmedik hata: {str(e)}. Devam ediliyor."