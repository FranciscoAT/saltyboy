# === Apps ===
db-migrate: docker-up-db


# === Install ===
install: install-bot install-web;

install-web:
	cd src/web
	poetry instal
	cd ..

install-bot:
	cd src/bot
	poetry install
	cd ..

# === Docker ===
docker-up-db:
	docker-compose up -d postgres