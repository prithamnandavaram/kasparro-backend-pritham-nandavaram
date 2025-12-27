.PHONY: up down test logs shell

up:
	docker-compose up --build -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose run --rm app pytest tests/ -v

shell:
	docker-compose run --rm app /bin/bash

# Utility to clean up
clean:
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
