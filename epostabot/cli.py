#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Komut Satırı Arayüzü (CLI)
GUI olmadan argümanlarla çalıştırma
"""

import argparse
import sys

from .config import BotConfig
from .bot import BotEngine


def create_parser() -> argparse.ArgumentParser:
    """Argüman ayrıştırıcısı oluştur"""
    parser = argparse.ArgumentParser(
        description="E-posta Bot - Otomatik e-posta kayıt botu",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  %(prog)s -p italyavize -s 100 -c 10 -w sifre123
  %(prog)s --prefix test --start 1 --count 5 --password pass --headless
  %(prog)s -p demo -s 50 -c 3 -w pass123 --url https://example.com/login
        """
    )
    
    # Zorunlu argümanlar
    required = parser.add_argument_group("Zorunlu argümanlar")
    required.add_argument(
        "-p", "--prefix",
        type=str,
        required=True,
        help="E-posta prefix'i (örn: italyavize)"
    )
    required.add_argument(
        "-w", "--password",
        type=str,
        required=True,
        help="E-posta şifresi"
    )
    
    # Opsiyonel argümanlar
    optional = parser.add_argument_group("Opsiyonel argümanlar")
    optional.add_argument(
        "-s", "--start",
        type=int,
        default=100,
        help="Başlangıç numarası (varsayılan: 100)"
    )
    optional.add_argument(
        "-c", "--count",
        type=int,
        default=10,
        help="E-posta sayısı (varsayılan: 10)"
    )
    optional.add_argument(
        "-d", "--domain",
        type=str,
        default="@gmail.com",
        help="E-posta domain'i (varsayılan: @gmail.com)"
    )
    optional.add_argument(
        "--headless",
        action="store_true",
        help="Tarayıcıyı görünmez modda çalıştır"
    )
    optional.add_argument(
        "--url",
        type=str,
        default="https://win-webb.wlsrv.com/login_up.php",
        help="Hedef login URL'i"
    )
    optional.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="İşlemler arası bekleme süresi (saniye)"
    )
    optional.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Sayfa yükleme zaman aşımı (saniye)"
    )
    optional.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Detaylı çıktı"
    )
    optional.add_argument(
        "--dry-run",
        action="store_true",
        help="Gerçek işlem yapmadan e-posta listesini göster"
    )
    
    return parser


def run_cli(args=None) -> int:
    """CLI uygulamasını çalıştır"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # Yapılandırma oluştur
    config = BotConfig(
        prefix=parsed_args.prefix,
        password=parsed_args.password,
        start_number=parsed_args.start,
        count=parsed_args.count,
        email_domain=parsed_args.domain,
        target_url=parsed_args.url,
        headless=parsed_args.headless,
        timeout=parsed_args.timeout,
        delay_between_logins=parsed_args.delay
    )
    
    # Doğrulama
    is_valid, error = config.validate()
    if not is_valid:
        print(f"Hata: {error}")
        return 1
    
    # Özet göster
    print("=" * 50)
    print("E-posta Bot - CLI Modu")
    print("=" * 50)
    print(f"Prefix: {config.prefix}")
    print(f"Aralık: {config.prefix}{config.start_number} - {config.prefix}{config.start_number + config.count - 1}")
    print(f"Toplam: {config.count} e-posta")
    print(f"Domain: {config.email_domain}")
    print(f"Hedef URL: {config.target_url}")
    print(f"Headless: {'Evet' if config.headless else 'Hayır'}")
    print("=" * 50)
    
    # Dry-run modu
    if parsed_args.dry_run:
        print("\n[DRY-RUN] Oluşturulacak e-postalar:")
        for email in config.get_all_emails():
            print(f"  - {email}")
        return 0
    
    # Bot'u çalıştır
    print("\nBot başlatılıyor...\n")
    
    def logger(msg: str):
        if parsed_args.verbose or msg.startswith("---") or msg.startswith("===") or "✓" in msg or "✗" in msg:
            print(msg)
    
    engine = BotEngine(config, logger=logger)
    
    try:
        results = engine.run()
        
        # Sonuç özeti
        print("\n" + "=" * 50)
        print("SONUÇ")
        print("=" * 50)
        print(f"Toplam: {results['total']}")
        print(f"Başarılı: {results['success']}")
        print(f"Başarısız: {results['failed']}")
        
        return 0 if results['failed'] == 0 else 1
        
    except KeyboardInterrupt:
        print("\n\nKullanıcı tarafından durduruldu.")
        return 130
    except Exception as e:
        print(f"\nKritik hata: {e}")
        return 1
