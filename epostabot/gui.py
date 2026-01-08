#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5 Grafik Arayüzü
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QPushButton, QTextEdit, QGroupBox,
    QMessageBox, QCheckBox
)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont

from .config import BotConfig
from .bot import BotEngine


class BotWorker(QThread):
    """Arka planda çalışan bot thread'i"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    
    def __init__(self, config: BotConfig, panel_email: str, panel_password: str):
        super().__init__()
        self.config = config
        self.panel_email = panel_email
        self.panel_password = panel_password
        self.engine: BotEngine = None
    
    def run(self):
        """Bot çalışma döngüsü"""
        self.engine = BotEngine(
            self.config, 
            logger=self.log_signal.emit,
            panel_email=self.panel_email,
            panel_password=self.panel_password
        )
        results = self.engine.run()
        self.finished_signal.emit(results)
    
    def stop(self):
        """Bot'u durdur"""
        if self.engine:
            self.engine.running = False


class MainWindow(QMainWindow):
    """Ana pencere"""
    
    def __init__(self):
        super().__init__()
        self.bot_worker = None
        self.init_ui()
    
    def init_ui(self):
        """UI bileşenlerini oluştur"""
        self.setWindowTitle("E-posta Bot")
        self.setMinimumSize(650, 650)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title_label = QLabel("E-posta Kayıt Botu")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title_label)
        
        # ===== PANEL GİRİŞ GRUBU =====
        panel_group = QGroupBox("1. Panel Giriş Bilgileri")
        panel_layout = QVBoxLayout(panel_group)
        
        # Panel E-posta
        panel_email_layout = QHBoxLayout()
        panel_email_label = QLabel("Panel E-posta:")
        panel_email_label.setMinimumWidth(120)
        self.panel_email_input = QLineEdit()
        self.panel_email_input.setPlaceholderText("Panel giriş e-postası")
        panel_email_layout.addWidget(panel_email_label)
        panel_email_layout.addWidget(self.panel_email_input)
        panel_layout.addLayout(panel_email_layout)
        
        # Panel Şifre
        panel_password_layout = QHBoxLayout()
        panel_password_label = QLabel("Panel Şifre:")
        panel_password_label.setMinimumWidth(120)
        self.panel_password_input = QLineEdit()
        self.panel_password_input.setEchoMode(QLineEdit.Password)
        self.panel_password_input.setPlaceholderText("Panel giriş şifresi")
        panel_password_layout.addWidget(panel_password_label)
        panel_password_layout.addWidget(self.panel_password_input)
        panel_layout.addLayout(panel_password_layout)
        
        layout.addWidget(panel_group)
        
        # ===== EMAIL OLUŞTURMA GRUBU =====
        email_group = QGroupBox("2. Oluşturulacak E-postalar")
        email_layout = QVBoxLayout(email_group)
        
        # E-posta prefix
        prefix_layout = QHBoxLayout()
        prefix_label = QLabel("E-posta Prefix:")
        prefix_label.setMinimumWidth(120)
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("örn: italyavize")
        prefix_layout.addWidget(prefix_label)
        prefix_layout.addWidget(self.prefix_input)
        email_layout.addLayout(prefix_layout)
        
        # Başlangıç numarası
        start_num_layout = QHBoxLayout()
        start_num_label = QLabel("Başlangıç No:")
        start_num_label.setMinimumWidth(120)
        self.start_num_input = QSpinBox()
        self.start_num_input.setRange(1, 99999)
        self.start_num_input.setValue(100)
        start_num_layout.addWidget(start_num_label)
        start_num_layout.addWidget(self.start_num_input)
        start_num_layout.addStretch()
        email_layout.addLayout(start_num_layout)
        
        # E-posta sayısı
        count_layout = QHBoxLayout()
        count_label = QLabel("E-posta Sayısı:")
        count_label.setMinimumWidth(120)
        self.count_input = QSpinBox()
        self.count_input.setRange(1, 100)
        self.count_input.setValue(10)
        count_layout.addWidget(count_label)
        count_layout.addWidget(self.count_input)
        count_layout.addStretch()
        email_layout.addLayout(count_layout)
        
        # Yeni hesapların şifresi
        new_password_layout = QHBoxLayout()
        new_password_label = QLabel("Yeni Şifre:")
        new_password_label.setMinimumWidth(120)
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setPlaceholderText("Oluşturulacak hesapların şifresi")
        new_password_layout.addWidget(new_password_label)
        new_password_layout.addWidget(self.new_password_input)
        email_layout.addLayout(new_password_layout)
        
        layout.addWidget(email_group)
        
        # ===== SEÇENEKLER =====
        options_group = QGroupBox("Seçenekler")
        options_layout = QVBoxLayout(options_group)
        
        # Headless modu
        self.headless_checkbox = QCheckBox("Headless Mod (Tarayıcı görünmez)")
        options_layout.addWidget(self.headless_checkbox)
        
        layout.addWidget(options_group)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Başlat")
        self.start_button.setMinimumHeight(40)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.start_button.clicked.connect(self.start_bot)
        
        self.stop_button = QPushButton("Durdur")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.stop_button.clicked.connect(self.stop_bot)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        # Log alanı
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Monaco", 10))
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
    
    def _create_config(self) -> BotConfig:
        """UI'dan yapılandırma oluştur"""
        return BotConfig(
            prefix=self.prefix_input.text().strip(),
            password=self.new_password_input.text(),
            start_number=self.start_num_input.value(),
            count=self.count_input.value(),
            headless=self.headless_checkbox.isChecked()
        )
    
    def start_bot(self):
        """Bot'u başlat"""
        panel_email = self.panel_email_input.text().strip()
        panel_password = self.panel_password_input.text()
        
        if not panel_email:
            QMessageBox.warning(self, "Uyarı", "Panel e-postası giriniz!")
            return
        
        if not panel_password:
            QMessageBox.warning(self, "Uyarı", "Panel şifresi giriniz!")
            return
        
        config = self._create_config()
        
        # Doğrulama
        is_valid, error = config.validate()
        if not is_valid:
            QMessageBox.warning(self, "Uyarı", error)
            return
        
        self.log_text.clear()
        self.log_text.append(f"Bot başlatılıyor...")
        self.log_text.append(f"Panel E-posta: {panel_email}")
        self.log_text.append(f"Prefix: {config.prefix}")
        self.log_text.append(f"Aralık: {config.prefix}{config.start_number} - {config.prefix}{config.start_number + config.count - 1}")
        self.log_text.append(f"Toplam: {config.count} e-posta oluşturulacak")
        self.log_text.append(f"Headless: {'Evet' if config.headless else 'Hayır'}")
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        self.bot_worker = BotWorker(config, panel_email, panel_password)
        self.bot_worker.log_signal.connect(self.append_log)
        self.bot_worker.finished_signal.connect(self.bot_finished)
        self.bot_worker.start()
    
    def stop_bot(self):
        """Bot'u durdur"""
        if self.bot_worker:
            self.bot_worker.stop()
            self.append_log("Durduruluyor...")
    
    def bot_finished(self, results: dict):
        """Bot tamamlandığında"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
    
    def append_log(self, message: str):
        """Log mesajı ekle"""
        self.log_text.append(message)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


def run_gui():
    """GUI uygulamasını başlat"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    return app.exec_()
