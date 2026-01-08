# E-posta Bot

PyQt5 UI ve Selenium ile otomatik e-posta kayıt botu.

## Proje Yapısı

```
epostabot/
├── main.py                 # Ana giriş noktası (GUI/CLI)
├── requirements.txt        # Python bağımlılıkları
├── Dockerfile              # Docker image tanımı
├── docker-compose.yml      # Docker Compose yapılandırması
├── Makefile                # Komut kısayolları
└── epostabot/              # Ana modül
    ├── __init__.py
    ├── config.py           # Yapılandırma sınıfı
    ├── bot.py              # Selenium bot motoru
    ├── gui.py              # PyQt5 arayüzü
    └── cli.py              # Komut satırı arayüzü
```

## Kurulum

### Yerel Kurulum

```bash
# Bağımlılıkları kur
make local-install

# GUI ile çalıştır
make local-run

# CLI ile çalıştır
python main.py --cli -p italyavize -w sifre123 -s 100 -c 10
```

### Docker ile Kurulum

```bash
make build
make run
```

## Kullanım Modları

### GUI Modu (Varsayılan)

```bash
python main.py
```

### CLI Modu

```bash
# Temel kullanım
python main.py --cli -p italyavize -w sifre123 -s 100 -c 10

# Headless mod
python main.py --cli -p italyavize -w sifre123 --headless

# Dry-run (e-posta listesini göster)
python main.py --cli -p italyavize -w sifre123 -c 5 --dry-run

# Tüm seçenekler
python main.py --cli --help
```

### CLI Argümanları

| Argüman | Kısa | Açıklama | Varsayılan |
|---------|------|----------|------------|
| `--prefix` | `-p` | E-posta prefix'i | (zorunlu) |
| `--password` | `-w` | Şifre | (zorunlu) |
| `--start` | `-s` | Başlangıç numarası | 100 |
| `--count` | `-c` | E-posta sayısı | 10 |
| `--domain` | `-d` | E-posta domain | @gmail.com |
| `--headless` | | Tarayıcı görünmez mod | false |
| `--url` | | Hedef login URL | win-webb.wlsrv.com |
| `--delay` | | İşlemler arası bekleme (sn) | 2.0 |
| `--timeout` | | Sayfa yükleme timeout (sn) | 10 |
| `--verbose` | `-v` | Detaylı çıktı | false |
| `--dry-run` | | Sadece e-posta listesi göster | false |

## Örnekler

```bash
# 10 e-posta oluştur: italyavize100 - italyavize109
python main.py --cli -p italyavize -s 100 -c 10 -w sifre123

# Headless modda çalıştır
python main.py --cli -p test -s 1 -c 5 -w pass --headless

# Farklı domain kullan
python main.py --cli -p user -s 1 -c 3 -w pass -d @outlook.com

# Özel URL kullan
python main.py --cli -p demo -s 1 -c 2 -w pass --url https://example.com/login
```

## Docker Komutları

```bash
make build         # Docker image oluştur
make run           # Container'ı çalıştır
make run-detached  # Arka planda çalıştır
make stop          # Durdur
make clean         # Temizle
make logs          # Logları göster
make shell         # Container'a bağlan
make rebuild       # Yeniden oluştur ve çalıştır
```

## Notlar

- macOS'ta Docker GUI desteği için XQuartz gereklidir
- Linux'ta `xhost +local:docker` komutu gerekebilir
- CLI modu GUI bağımlılıkları olmadan da çalışabilir
