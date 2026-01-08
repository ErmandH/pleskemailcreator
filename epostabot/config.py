#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yapılandırma modülü
Tüm ayarlar burada merkezi olarak yönetilir
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class BotConfig:
    """Bot yapılandırma sınıfı"""
    
    # E-posta ayarları
    prefix: str = ""
    password: str = ""
    start_number: int = 100
    count: int = 10
    email_domain: str = "@gmail.com"
    
    # Hedef site ayarları
    target_url: str = "https://win-webb.wlsrv.com/login_up.php"
    username_selector: str = "#login_name"
    password_selector: str = "#passwd"
    submit_selector: str = "button[data-action='log-in']"
    
    # Tarayıcı ayarları
    headless: bool = False
    timeout: int = 10
    delay_between_logins: float = 2.0
    
    # Chrome ayarları
    chrome_options: list = None
    
    def __post_init__(self):
        if self.chrome_options is None:
            self.chrome_options = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ]
    
    def get_email_prefix(self, index: int) -> str:
        """Belirtilen indeks için e-posta prefix'i oluştur (@ öncesi kısım)"""
        number = self.start_number + index
        return f"{self.prefix}{number}"
    
    def get_email(self, index: int) -> str:
        """Belirtilen indeks için tam e-posta adresi oluştur (log için)"""
        return f"{self.get_email_prefix(index)}{self.email_domain}"
    
    def get_all_emails(self) -> list:
        """Tüm e-posta adreslerinin listesini döndür"""
        return [self.get_email(i) for i in range(self.count)]
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Yapılandırmayı doğrula"""
        if not self.prefix:
            return False, "E-posta prefix'i boş olamaz"
        if not self.password:
            return False, "Şifre boş olamaz"
        if self.count < 1:
            return False, "E-posta sayısı en az 1 olmalı"
        if self.start_number < 0:
            return False, "Başlangıç numarası 0'dan küçük olamaz"
        return True, None
