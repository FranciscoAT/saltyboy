# === Apps ===
run-bot: db-migrate
	cd src/bot && poetry run python main.py 

run-web: db-migrate
	cd src/web && poetry run python main.py

run-extension:
	cd src/extension && npm run dev

# === Builds ===
build-extension:
	cd src/extension && npm run build

# === Database ===
db-migrate: docker-up-db
	cd src/bot && poetry run alembic upgrade head

# === Install ===
install: install-bot install-web install-extension;

install-web:
	cd src/web && poetry install --no-root

install-bot:
	cd src/bot && poetry install --no-root

install-extension:
	cd src/extension && npm install

# === Docker ===
docker-up:
	docker-compose up -d

docker-build:
	docker-compose build
	

docker-up-db:
	docker-compose -f docker-compose.local.yml up -d postgres

# === Linting ===
lint: lint-black lint-isort lint-mypy lint-pycln lint-ruff lint-prettier;

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
	cd src/bot && poetry run black --check src/
	cd src/bot && poetry run black --check alembic/
	cd src/bot && poetry run black --check main.py
lint-black-web:
	cd src/web && poetry run black --check src/
	cd src/web && poetry run black --check main.py

lint-isort-bot:
	cd src/bot && poetry run isort --check src/
	cd src/bot && poetry run isort --check alembic/
	cd src/bot && poetry run isort --check main.py
lint-isort-web:
	cd src/web && poetry run isort --check src/
	cd src/web && poetry run isort --check main.py

lint-mypy-bot:
	cd src/bot && poetry run mypy src/
	cd src/bot && poetry run mypy alembic/
	cd src/bot && poetry run mypy main.py
lint-mypy-web:
	cd src/web && poetry run mypy src/
	cd src/web && poetry run mypy main.py

lint-pycln-bot:
	cd src/bot && poetry run pycln --all --check src/
	cd src/bot && poetry run pycln --all --check alembic/
	cd src/bot && poetry run pycln --all --check main.py
lint-pycln-web:
	cd src/web && poetry run pycln --all src/
	cd src/web && poetry run pycln --all main.py

lint-pylint-bot:
	cd src/bot && poetry run pylint src/ || poetry run pylint-exit --error-fail $$?
	cd src/bot && poetry run pylint alembic/ || poetry run pylint-exit --error-fail $$?
	cd src/bot && poetry run pylint main.py || poetry run pylint-exit --error-fail $$?
lint-pylint-web:
	cd src/web && poetry run pylint src/ || poetry run pylint-exit --error-fail $$?
	cd src/web && poetry run pylint main.py || poetry run pylint-exit --error-fail $$?

lint-ruff-bot:
	cd src/bot && poetry run ruff src/
	cd src/bot && poetry run ruff alembic/
	cd src/bot && poetry run ruff main.py
lint-ruff-web:
	cd src/web && poetry run ruff src/
	cd src/web && poetry run ruff main.py

lint-prettier-extension:
	cd src/extension && npx prettier src/ --check

# === Formatting ===
format: format-black format-isort format-pycln format-prettier;

format-web: format-black-web format-isort-web format-pycln-web;
format-bot: format-black-bot format-isort-bot format-pycln-bot;
format-extension: format-prettier-extension;

format-black: format-black-bot format-black-web;
format-isort: format-isort-bot format-isort-web;
format-pycln: format-pycln-bot format-pycln-web;
format-prettier: format-prettier-extension;

format-black-bot:
	cd src/bot && poetry run black src/
	cd src/bot && poetry run black alembic/
	cd src/bot && poetry run black main.py
format-black-web:
	cd src/web && poetry run black src/
	cd src/web && poetry run black main.py

format-isort-bot:
	cd src/bot && poetry run isort src/
	cd src/bot && poetry run isort alembic/
	cd src/bot && poetry run isort main.py
format-isort-web:
	cd src/web && poetry run isort src/
	cd src/web && poetry run isort main.py

format-pycln-bot:
	cd src/bot && poetry run pycln --all src/
	cd src/bot && poetry run pycln --all alembic/
	cd src/bot && poetry run pycln --all main.py
format-pycln-web:
	cd src/web && poetry run pycln src/
	cd src/web && poetry run pycln main.py

format-prettier-extension:
	cd src/extension && npx prettier src --write