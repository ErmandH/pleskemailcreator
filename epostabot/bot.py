#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium Bot Motoru
Tarayıcı otomasyonu için temel sınıf
"""

import time
import os
import requests
from typing import Callable, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from .config import BotConfig


class BotEngine:
    """Selenium tabanlı bot motoru"""
    
    def __init__(
        self, 
        config: BotConfig, 
        logger: Optional[Callable[[str], None]] = None,
        panel_email: str = "",
        panel_password: str = ""
    ):
        """
        Bot motorunu başlat
        
        Args:
            config: Bot yapılandırması
            logger: Log fonksiyonu (opsiyonel, varsayılan: print)
            panel_email: Panel giriş e-postası
            panel_password: Panel giriş şifresi
        """
        self.config = config
        self.logger = logger or print
        self.panel_email = panel_email
        self.panel_password = panel_password
        self.driver: Optional[webdriver.Chrome] = None
        self.running = False
    
    def log(self, message: str):
        """Log mesajı gönder"""
        self.logger(message)
    
    def _create_driver(self) -> webdriver.Chrome:
        """Chrome WebDriver oluştur"""
        chrome_options = Options()
        
        for option in self.config.chrome_options:
            chrome_options.add_argument(option)
        
        if self.config.headless:
            chrome_options.add_argument("--headless=new")
        
        # Docker'da Chromium kullan
        chrome_bin = os.environ.get("CHROME_BIN")
        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
        
        if chrome_bin and os.path.exists(chrome_bin):
            chrome_options.binary_location = chrome_bin
        
        if chromedriver_path and os.path.exists(chromedriver_path):
            service = Service(chromedriver_path)
        else:
            # Yerel geliştirmede ChromeDriverManager kullan
            try:
                driver_path = ChromeDriverManager().install()
                self.log(f"ChromeDriver path: {driver_path}")
                
                # Doğru chromedriver binary'sini bul
                driver_dir = os.path.dirname(driver_path)
                actual_driver = None
                
                for f in os.listdir(driver_dir):
                    full_path = os.path.join(driver_dir, f)
                    # chromedriver binary'si (THIRD_PARTY değil, executable)
                    if f == "chromedriver" and os.path.isfile(full_path):
                        actual_driver = full_path
                        break
                
                if actual_driver is None:
                    # Bir üst dizinde ara
                    parent_dir = os.path.dirname(driver_dir)
                    for root, dirs, files in os.walk(parent_dir):
                        for f in files:
                            if f == "chromedriver":
                                full_path = os.path.join(root, f)
                                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                                    actual_driver = full_path
                                    break
                        if actual_driver:
                            break
                
                if actual_driver:
                    self.log(f"Kullanılan ChromeDriver: {actual_driver}")
                    service = Service(actual_driver)
                else:
                    raise Exception(f"chromedriver binary bulunamadı: {driver_dir}")
                    
            except Exception as e:
                self.log(f"ChromeDriver kurulum hatası: {e}")
                raise
        
        return webdriver.Chrome(service=service, options=chrome_options)
    
    def start(self):
        """Tarayıcıyı başlat"""
        self.log("Chrome başlatılıyor...")
        self.driver = self._create_driver()
        self.running = True
        self.log("Chrome başlatıldı!")
    
    def stop(self):
        """Tarayıcıyı kapat"""
        self.running = False
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.log("Chrome kapatıldı.")
    
    def panel_login(self) -> bool:
        """
        Panel'e giriş yap
        
        Returns:
            True: başarılı, False: başarısız
        """
        if not self.driver:
            self.log("Hata: Tarayıcı başlatılmamış!")
            return False
        
        try:
            # Panel sayfasına git
            self.log(f"Panel sayfasına gidiliyor: {self.config.target_url}")
            self.driver.get(self.config.target_url)
            
            wait = WebDriverWait(self.driver, self.config.timeout)
            
            # Kullanıcı adı alanı
            self.log(f"Panel kullanıcı adı giriliyor: {self.panel_email}")
            username_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.config.username_selector))
            )
            username_field.clear()
            username_field.send_keys(self.panel_email)
            
            # Şifre alanı
            self.log("Panel şifresi giriliyor...")
            password_field = self.driver.find_element(By.CSS_SELECTOR, self.config.password_selector)
            password_field.clear()
            password_field.send_keys(self.panel_password)
            
            # Giriş butonu
            self.log("Oturum aç butonuna tıklanıyor...")
            login_button = self.driver.find_element(By.CSS_SELECTOR, self.config.submit_selector)
            login_button.click()
            
            # Giriş başarılı mı kontrol et
            time.sleep(3)  # Sayfa yüklenmesini bekle
            
            self.log("✓ Panel girişi başarılı!")
            return True
            
        except TimeoutException:
            self.log("✗ Zaman aşımı: Panel elementleri bulunamadı")
            return False
        except WebDriverException as e:
            self.log(f"✗ Tarayıcı hatası: {str(e)}")
            return False
        except Exception as e:
            self.log(f"✗ Panel giriş hatası: {str(e)}")
            return False
    
    def wait_for_dashboard(self) -> bool:
        """
        Login sonrası dashboard sayfasını bekle
        
        Returns:
            True: başarılı, False: zaman aşımı
        """
        try:
            self.log("Dashboard sayfası bekleniyor (max 30 sn)...")
            wait = WebDriverWait(self.driver, 30)
            
            # URL'in /smb/web/view olmasını bekle
            wait.until(EC.url_contains("/smb/web/view"))
            self.log("✓ Dashboard sayfasına ulaşıldı!")
            return True
            
        except TimeoutException:
            self.log("✗ Dashboard sayfası yüklenemedi (30 sn zaman aşımı)")
            return False
        except Exception as e:
            self.log(f"✗ Dashboard bekleme hatası: {str(e)}")
            return False
    
    def create_email(self, email: str) -> bool:
        """
        Panelde yeni e-posta oluştur
        
        Args:
            email: Oluşturulacak e-posta adresi (sadece @ öncesi kısım)
            
        Returns:
            True: başarılı, False: başarısız
        """
        if not self.driver:
            self.log("Hata: Tarayıcı başlatılmamış!")
            return False
        
        try:
            self.log(f"E-posta oluşturuluyor: {email}")
            
            # 1. E-posta oluşturma sayfasına git
            create_url = "https://win-webb.wlsrv.com/smb/email-address/create"
            self.log(f"E-posta oluşturma sayfasına gidiliyor: {create_url}")
            self.driver.get(create_url)
            
            wait = WebDriverWait(self.driver, 30)
            
            # 2. E-posta adresi alanını doldur
            self.log("E-posta adresi giriliyor...")
            email_input = wait.until(
                EC.presence_of_element_located((By.ID, "general-generalSection-name"))
            )
            email_input.clear()
            email_input.send_keys(email)
            
            # 3. Domain seçimi (varsayılan olarak ilk option seçili kalır)
            # İsterseniz özel domain seçebilirsiniz
            # domain_select = Select(self.driver.find_element(By.ID, "general-generalSection-domain"))
            # domain_select.select_by_visible_text("phoenixtur.com")
            
            # 4. "Plesk'te oturum açmak için kullanılabilir" checkbox'ını kaldır
            self.log("Oturum açma seçeneği kapatılıyor...")
            login_checkbox = self.driver.find_element(By.ID, "general-generalSection-loginAsUser")
            if login_checkbox.is_selected():
                login_checkbox.click()
                time.sleep(0.3)
            
            # 5. Şifre gir
            self.log("Şifre giriliyor...")
            password_field = self.driver.find_element(By.ID, "general-generalSection-password")
            password_field.clear()
            password_field.send_keys(self.config.password)
            
            # 6. Şifre onayı
            password_confirm = self.driver.find_element(By.ID, "general-generalSection-passwordConfirmation")
            password_confirm.clear()
            password_confirm.send_keys(self.config.password)
            
            # 7. Posta kutusu boyutu - "Başka bir boyut" seç ve 30 MB ayarla
            self.log("Posta kutusu boyutu ayarlanıyor (30 MB)...")
            
            # "Başka bir boyut" radio butonuna tıkla
            specific_radio = self.driver.find_element(By.ID, "general-generalSection-mboxQuotaValue-specific")
            specific_radio.click()
            time.sleep(0.3)
            
            # Boyut değerini gir
            size_input = self.driver.find_element(By.ID, "general-generalSection-mboxQuotaValue-specific-input")
            size_input.clear()
            size_input.send_keys("30")
            
            # MB seç (multiplier dropdown)
            from selenium.webdriver.support.ui import Select
            multiplier_select = Select(self.driver.find_element(By.ID, "general-generalSection-mboxQuotaValue-specific-multiplier"))
            multiplier_select.select_by_value("1048576")  # MB değeri
            
            # 8. Tamam butonuna tıkla
            self.log("Tamam butonuna tıklanıyor...")
            submit_button = self.driver.find_element(By.ID, "btn-send")
            submit_button.click()
            
            # 9. E-posta listesi sayfasını bekle (max 60 sn)
            self.log("E-posta listesi sayfası bekleniyor (max 60 sn)...")
            wait_long = WebDriverWait(self.driver, 60)
            wait_long.until(EC.url_contains("/smb/email-address/list"))
            
            self.log(f"✓ {email} başarıyla oluşturuldu!")
            return True
            
        except TimeoutException as e:
            error_msg = f"Zaman aşımı hatası: {str(e)}"
            self.log(f"✗ {error_msg}")
            self._show_error_alert(f"E-posta oluşturma başarısız!\n\n{error_msg}\n\nMevcut URL: {self.driver.current_url}")
            return False
        except WebDriverException as e:
            error_msg = f"Tarayıcı hatası: {str(e)}"
            self.log(f"✗ {error_msg}")
            self._show_error_alert(f"E-posta oluşturma başarısız!\n\n{error_msg}")
            return False
        except Exception as e:
            import traceback
            error_msg = f"Beklenmeyen hata: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            self.log(f"✗ {error_msg}")
            self._show_error_alert(f"E-posta oluşturma başarısız!\n\n{error_msg}")
            return False
    
    def _show_error_alert(self, message: str):
        """
        JavaScript alert ile hata mesajı göster
        
        Args:
            message: Gösterilecek hata mesajı
        """
        try:
            if self.driver:
                # Mesajı JavaScript için escape et
                escaped_message = message.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
                self.driver.execute_script(f"alert('{escaped_message}');")
        except Exception as e:
            self.log(f"Alert gösterilemedi: {str(e)}")
    
    def register_email_to_mailpanel(self, email_address: str, password: str) -> bool:
        """
        Oluşturulan e-postayı mailpanel API'sine kaydet
        
        Args:
            email_address: Tam e-posta adresi (örn: test100@mailpanel.phoenixtur.com)
            password: E-posta şifresi
            
        Returns:
            True: başarılı, False: başarısız
        """
        api_url = "https://mailpanel2.phoenixtur.com/api/email-accounts/"
        
        # E-posta adresinden name oluştur
        email_name = email_address.split("@")[0]
        
        payload = {
            "name": f"Phoenix {email_name}",
            "email_address": email_address,
            "password": password,
            "check_interval": 5,
            "is_active": True
        }
        
        try:
            self.log(f"Mailpanel API'ye kayıt gönderiliyor: {email_address}")
            
            response = requests.post(
                api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                self.log(f"✓ Mailpanel'e kaydedildi: {email_address}")
                return True
            else:
                self.log(f"✗ Mailpanel API hatası: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.log(f"✗ Mailpanel API zaman aşımı: {email_address}")
            return False
        except requests.exceptions.RequestException as e:
            self.log(f"✗ Mailpanel API bağlantı hatası: {str(e)}")
            return False
        except Exception as e:
            self.log(f"✗ Mailpanel kayıt hatası: {str(e)}")
            return False
    
    def run(self) -> dict:
        """
        Bot'u çalıştır
        1. Önce panele giriş yap
        2. Sonra e-postaları oluştur
        
        Returns:
            Sonuç istatistikleri
        """
        results = {
            "total": self.config.count,
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        try:
            self.start()
            
            # 1. Panel girişi
            self.log("\n=== ADIM 1: Panel Girişi ===")
            if not self.panel_login():
                self.log("Panel girişi başarısız! Bot durduruluyor.")
                return results
            
            # 2. Dashboard sayfasını bekle
            self.log("\n=== ADIM 2: Dashboard Bekleniyor ===")
            if not self.wait_for_dashboard():
                self.log("Dashboard sayfasına ulaşılamadı! Bot durduruluyor.")
                return results
            
            # 3. E-postaları oluştur
            self.log("\n=== ADIM 3: E-posta Oluşturma ===")
            
            for i in range(self.config.count):
                if not self.running:
                    self.log("Bot durduruldu!")
                    break
                
                email = self.config.get_email(i)  # Tam email (log ve API için)
                email_prefix = self.config.get_email_prefix(i)  # Sadece prefix (input için)
                self.log(f"\n--- E-posta {i+1}/{self.config.count}: {email} ---")
                
                success = self.create_email(email_prefix)
                
                # Başarılı oluşturma sonrası Mailpanel'e kaydet
                mailpanel_success = False
                if success:
                    # Domain'i config'den al (varsayılan mailpanel.phoenixtur.com)
                    full_email = f"{email_prefix}@mailpanel.phoenixtur.com"
                    mailpanel_success = self.register_email_to_mailpanel(
                        full_email, 
                        self.config.password
                    )
                
                results["details"].append({
                    "email": email,
                    "success": success,
                    "mailpanel_registered": mailpanel_success
                })
                
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                
                # Sonraki işlem için bekle
                if i < self.config.count - 1 and self.running:
                    time.sleep(self.config.delay_between_logins)
            
            self.log(f"\n=== Bot tamamlandı! Başarılı: {results['success']}, Başarısız: {results['failed']} ===")
            self.log("Tarayıcı açık bırakıldı. Manuel olarak kapatabilirsiniz.")
            
        except Exception as e:
            self.log(f"Kritik hata: {str(e)}")
            # Sadece hata durumunda tarayıcıyı kapat
            self.stop()
        
        return results
