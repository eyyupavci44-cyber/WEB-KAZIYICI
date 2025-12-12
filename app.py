# app.py (NİHAİ VERSİYON - Dairesel İçe Aktarma Çözüldü)

import time
import json
import os
from flask import Flask, render_template, request, session, send_file, redirect, url_for
from scrapers.basic_scraper import perform_scrape
from scrapers.advanced_scraper import perform_advanced_scrape 
from utils.validator import check_robots_txt 
# init_db çağrısı buradan kaldırıldı
from utils.data_handler import log_scrape_to_db, get_history, convert_to_csv, convert_to_json 
from io import BytesIO

# --- Flask Uygulama Ayarları ---
app = Flask(__name__)
# Session kullanmak için gizli anahtar
app.secret_key = os.environ.get('SECRET_KEY', 'cok_gizli_anahtar_12345') 


# KAZIMA İŞLEMİNİ YÜRÜTEN ANA FONKSİYON
def execute_scrape(url, selectors, delay, dynamic_mode):
    """URL bazında etik kontrol ve kazıma işlemini yürütür. (Aşama 2 & 4)"""
    
    # 1. Etik Kontrol
    is_allowed, robot_message = check_robots_txt(url)
    
    if not is_allowed:
        error_message = f"Etik Hata: Kazıma işlemi robots.txt kuralları nedeniyle durduruldu. ({robot_message})"
        log_scrape_to_db(url, 403, 0, False, error_message)
        return [], 403, error_message

    # 2. Kazıma Modülünü Seçme ve Çalıştırma
    if dynamic_mode:
        # Dinamik Mod (Selenium)
        results, status_code, scraper_error = perform_advanced_scrape(url, selectors, delay)
    else:
        # Statik Mod (requests/bs4)
        results, status_code, scraper_error = perform_scrape(url, selectors, delay)
        
    # 3. Sonuç Kaydı (Aşama 3)
    if status_code != 200:
        final_error = scraper_error if scraper_error else f"Hata: HTTP Durum Kodu {status_code}."
        log_scrape_to_db(url, status_code, 0, False, final_error)
        return [], status_code, final_error
    else:
        log_scrape_to_db(url, status_code, len(results), True, "")
        return results, status_code, None


# ANA KAZIMA ROUTE (Toplu İşlem Yapar)
@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    error_message = None
    
    if request.method == 'POST':
        # Formdan Toplu URL, Seçiciler ve Mod seçimini al
        urls_input = request.form.get('url') 
        selectors_input = request.form.get('selectors')
        delay = request.form.get('delay', type=int) 
        # Dinamik Mod (Checkbox)
        dynamic_mode = request.form.get('dynamic_mode') == 'on' 
        
        if not urls_input or not selectors_input or delay is None:
            error_message = "Lütfen tüm gerekli alanları doldurun."
            return render_template('index.html', results=results, error_message=error_message)
        
        try:
            # URL'leri ayırma (Toplu İşleme Mantığı - Aşama 4)
            urls = [u.strip() for u in urls_input.replace('\r\n', '\n').split('\n') if u.strip()]
            selectors = [s.strip() for s in selectors_input.split(',')]
            
            if delay < 1: delay = 1
            
            all_results = []
            
            # --- TOPLU İŞLEME DÖNGÜSÜ ---
            for url in urls:
                single_results, status_code, error = execute_scrape(url, selectors, delay, dynamic_mode)
                
                # Tekil hataları toplar, ancak tüm işlem devam eder.
                if status_code != 200 and not error_message:
                    error_message = f"Bazı URL'lerde sorun oluştu. İlk Hata: {error}"
                    
                all_results.extend(single_results)
                
            results = all_results
            
            # Session'a Toplu Sonuçları Kaydet (İndirme için)
            if results:
                session['last_scrape_data'] = results
            else:
                session.pop('last_scrape_data', None)
                
        except Exception as e:
            error_message = f"Beklenmedik bir hata oluştu: {str(e)}"
            results = None
            session.pop('last_scrape_data', None)
            
    # Session'daki son veriyi arayüze gönder
    current_results = session.get('last_scrape_data', results)
    
    return render_template('index.html', results=current_results, error_message=error_message)


# TARİHÇE ROUTE
@app.route('/history')
def history():
    history_data = get_history()
    return render_template('history.html', history_data=history_data)

# İNDİRME ROUTE'LARI (CSV/JSON Çıktısı - Aşama 3)
@app.route('/download/<format>')
def download_data(format):
    data_to_download = session.get('last_scrape_data')
    
    if not data_to_download:
        return redirect(url_for('index', error_message='İndirilecek güncel veri bulunamadı.'))
        
    if format == 'csv':
        csv_data = convert_to_csv(data_to_download)
        buffer = BytesIO(csv_data.encode('utf-8'))
        return send_file(buffer, as_attachment=True, download_name='scrape_data.csv', mimetype='text/csv')
    
    elif format == 'json':
        json_data = convert_to_json(data_to_download)
        buffer = BytesIO(json_data.encode('utf-8'))
        return send_file(buffer, as_attachment=True, download_name='scrape_data.json', mimetype='application/json')
        
    else:
        return "Geçersiz indirme formatı", 400


# Uygulamayı başlat (Ana Giriş Noktası)
if __name__ == '__main__':
    # DÜZELTME: init_db çağrısı buraya taşındı.
    from utils.data_handler import init_db
    init_db() 
    
    # Loglama ve hata ayıklama için debug=True
    app.run(debug=True)