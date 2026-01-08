#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-posta Bot - Ana Giriş Noktası

Kullanım:
  GUI modu:    python main.py
  CLI modu:    python main.py --cli -p prefix -w sifre -s 100 -c 10
  Yardım:      python main.py --help
"""

import sys
import argparse


def main():
    """Ana giriş noktası"""
    
    # Basit argüman kontrolü - CLI mi GUI mi?
    parser = argparse.ArgumentParser(
        description="E-posta Bot",
        add_help=False
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="CLI modunda çalıştır (GUI yerine)"
    )
    parser.add_argument(
        "-h", "--help",
        action="store_true",
        help="Yardım mesajını göster"
    )
    
    # Sadece bilinen argümanları parse et
    known_args, remaining_args = parser.parse_known_args()
    
    if known_args.cli or known_args.help:
        # CLI modu
        from epostabot.cli import run_cli
        
        # --cli argümanını kaldır ve geri kalanını CLI'a gönder
        if known_args.help:
            remaining_args.append("--help")
        
        sys.exit(run_cli(remaining_args))
    else:
        # GUI modu
        try:
            from epostabot.gui import run_gui
            sys.exit(run_gui())
        except ImportError as e:
            print(f"GUI başlatılamadı: {e}")
            print("PyQt5 yüklü değil olabilir. CLI modunu deneyin:")
            print("  python main.py --cli --help")
            sys.exit(1)


if __name__ == "__main__":
    main()
