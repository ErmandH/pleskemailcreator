.PHONY: build run stop clean logs shell local-install local-run

# Docker komutları
build:
	docker-compose build

run:
	docker-compose up

run-detached:
	docker-compose up -d

stop:
	docker-compose down

clean:
	docker-compose down -v --rmi all

logs:
	docker-compose logs -f

shell:
	docker-compose exec epostabot /bin/bash

# Yerel geliştirme komutları
local-install:
	pip install -r requirements.txt

local-run:
	python main.py

# Docker image yeniden oluştur ve çalıştır
rebuild:
	docker-compose build --no-cache
	docker-compose up

# Yardım
help:
	@echo "Kullanılabilir komutlar:"
	@echo "  make build         - Docker image oluştur"
	@echo "  make run           - Container'ı çalıştır"
	@echo "  make run-detached  - Container'ı arka planda çalıştır"
	@echo "  make stop          - Container'ı durdur"
	@echo "  make clean         - Container ve image'ları temizle"
	@echo "  make logs          - Container loglarını göster"
	@echo "  make shell         - Container'a shell aç"
	@echo "  make local-install - Yerel bağımlılıkları kur"
	@echo "  make local-run     - Uygulamayı yerel olarak çalıştır"
	@echo "  make rebuild       - Image'ı yeniden oluştur ve çalıştır"
