FROM python:3.11-slim

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    libxi6 \
    libnss3 \
    libxss1 \
    libasound2t64 \
    libxtst6 \
    libgtk-3-0 \
    libgbm1 \
    libxkbcommon0 \
    # PyQt5 için gerekli
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libegl1 \
    libgl1 \
    libxkbcommon-x11-0 \
    fonts-liberation \
    xdg-utils \
    # Chrome için
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY . .

# Display ortam değişkeni
ENV DISPLAY=:99
ENV QT_QPA_PLATFORM=xcb
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Xvfb ile başlat
CMD ["sh", "-c", "Xvfb :99 -screen 0 1920x1080x24 & sleep 1 && python main.py"]
