sync:
    uv sync --frozen --python 3.12

serve:
    uv run --frozen bentoml serve careerpath.service:CareerPathService --host 127.0.0.1 --port 3000 --do-not-track

lint:
    uv run --frozen ruff check .

test:
    uv run --frozen pytest -q

check: lint test

demo: sync
    uv run --frozen pytest -q tests/test_e2e.py

docker-build:
    docker build --tag careerpath-mlops:local .

docker-run:
    docker run --rm --publish 3000:3000 careerpath-mlops:local
