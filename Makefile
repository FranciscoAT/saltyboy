# === Apps ===
run-bot: db-migrate
	cd applications/bot && poetry run python main.py
run-bot-log-file: db-migrate
	mkdir -p logs/bot
	cd applications/bot && poetry run python main.py --logs ../../logs/bot/
run-bot-debug: db-migrate
	cd applications/bot && poetry run python main.py --debug
run-bot-log-file-debug: db-migrate
	mkdir -p logs/bot
	cd applications/bot && poetry run python main.py --logs ../../logs/bot/ --debug

run-web: db-migrate
	cd applications/web && poetry run python main.py

run-extension:
	cd applications/extension && npm run dev

# === Builds ===
build-extension:
	cd applications/extension && npm run build

# === Database ===
db-migrate: docker-up-db
	cd applications/bot && poetry run alembic upgrade head

# === Install ===
install: install-bot install-web install-extension;

install-web:
	cd applications/web && poetry install --no-root

install-bot:
	cd applications/bot && poetry install --no-root

install-extension:
	cd applications/extension && npm install

# === Docker ===
docker-up:
	docker-compose up -d

docker-build:
	docker-compose build
	

docker-up-db:
	docker-compose -f docker-compose.local.yml up -d postgres

# === Linting ===
lint: lint-web lint-bot lint-extension;

lint-web: lint-black-web lint-isort-web lint-mypy-web lint-pycln-web lint-pylint-web lint-ruff-web;
lint-bot: lint-black-bot lint-isort-bot lint-mypy-bot lint-pycln-bot lint-pylint-bot lint-ruff-bot;
lint-extension: lint-prettier-extension;

lint-black: lint-black-bot lint-black-web;
lint-isort: lint-isort-bot lint-isort-web;
lint-mypy: lint-mypy-bot lint-mypy-web;
lint-pycln: lint-pycln-bot lint-pycln-web;
lint-pylint: lint-pylint-bot lint-pylint-web;
lint-ruff: lint-ruff-bot lint-ruff-web;
lint-prettier: lint-prettier-extension;


lint-black-bot:
	cd applications/bot && poetry run black --check src/
	cd applications/bot && poetry run black --check alembic/
	cd applications/bot && poetry run black --check main.py
lint-black-web:
	cd applications/web && poetry run black --check src/
	cd applications/web && poetry run black --check main.py

lint-isort-bot:
	cd applications/bot && poetry run isort --check src/
	cd applications/bot && poetry run isort --check alembic/
	cd applications/bot && poetry run isort --check main.py
lint-isort-web:
	cd applications/web && poetry run isort --check src/
	cd applications/web && poetry run isort --check main.py

lint-mypy-bot:
	cd applications/bot && poetry run mypy src/
	cd applications/bot && poetry run mypy alembic/
	cd applications/bot && poetry run mypy main.py
lint-mypy-web:
	cd applications/web && poetry run mypy src/
	cd applications/web && poetry run mypy main.py

lint-pycln-bot:
	cd applications/bot && poetry run pycln --all --check src/
	cd applications/bot && poetry run pycln --all --check alembic/
	cd applications/bot && poetry run pycln --all --check main.py
lint-pycln-web:
	cd applications/web && poetry run pycln --all --check src/
	cd applications/web && poetry run pycln --all --check main.py

lint-pylint-bot:
	cd applications/bot && poetry run pylint src/ || poetry run pylint-exit --error-fail $$?
	cd applications/bot && poetry run pylint main.py || poetry run pylint-exit --error-fail $$?
lint-pylint-web:
	cd applications/web && poetry run pylint src/ || poetry run pylint-exit --error-fail $$?
	cd applications/web && poetry run pylint main.py || poetry run pylint-exit --error-fail $$?

lint-ruff-bot:
	cd applications/bot && poetry run ruff src/
	cd applications/bot && poetry run ruff alembic/
	cd applications/bot && poetry run ruff main.py
lint-ruff-web:
	cd applications/web && poetry run ruff src/
	cd applications/web && poetry run ruff main.py

lint-prettier-extension:
	cd applications/extension && npx prettier src/ --check

# === Formatting ===
format: format-web format-bot format-extension;

format-web: format-black-web format-isort-web format-pycln-web;
format-bot: format-black-bot format-isort-bot format-pycln-bot;
format-extension: format-prettier-extension;

format-black: format-black-bot format-black-web;
format-isort: format-isort-bot format-isort-web;
format-pycln: format-pycln-bot format-pycln-web;
format-prettier: format-prettier-extension;

format-black-bot:
	cd applications/bot && poetry run black src/
	cd applications/bot && poetry run black alembic/
	cd applications/bot && poetry run black main.py
format-black-web:
	cd applications/web && poetry run black src/
	cd applications/web && poetry run black main.py

format-isort-bot:
	cd applications/bot && poetry run isort src/
	cd applications/bot && poetry run isort alembic/
	cd applications/bot && poetry run isort main.py
format-isort-web:
	cd applications/web && poetry run isort src/
	cd applications/web && poetry run isort main.py

format-pycln-bot:
	cd applications/bot && poetry run pycln --all src/
	cd applications/bot && poetry run pycln --all alembic/
	cd applications/bot && poetry run pycln --all main.py
format-pycln-web:
	cd applications/web && poetry run pycln src/
	cd applications/web && poetry run pycln main.py

format-prettier-extension:
	cd applications/extension && npx prettier src --write
