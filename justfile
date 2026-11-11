sync:
    uv sync --frozen --python 3.12

serve:
    uv run --frozen bentoml serve careerpath.service:CareerPathService --host 127.0.0.1 --port 3000 --do-not-track

lint:
    uv run --frozen ruff check .

test:
    uv run --frozen pytest -q

compile:
    uv run --frozen python -m compileall -q src scripts tests

check: lint test compile

demo: sync
    uv run --frozen pytest -q tests/test_e2e.py

load scenario="baseline" count="100" invalid_every="0":
    uv run --frozen python scripts/generate_load.py --scenario {{scenario}} --count {{count}} --invalid-every {{invalid_every}}

docker-build:
    docker build --tag careerpath-mlops:av2 .

docker-run volume="careerpath-av2-logs":
    docker run --rm --publish 127.0.0.1:3000:3000 --mount "type=volume,source={{volume}},target=/app/logs" careerpath-mlops:av2
