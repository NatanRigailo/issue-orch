.PHONY: up build run lint test clean

IMAGE := ghcr.io/natanrigailo/issue-orch

up:
	docker compose -f deploy/docker-compose.yml up -d

down:
	docker compose -f deploy/docker-compose.yml down

build:
	docker build -t $(IMAGE):local .

run:
	python main.py

lint:
	flake8 app/ main.py
	bandit -r app/ -ll

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
