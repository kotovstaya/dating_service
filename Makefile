#!/usr/bin/make

dev_start:
	docker compose -f docker-compose.dev.yaml up

dev_stop: 
	docker compose -f docker-compose.dev.yaml down
	docker rmi telegram_bot
	docker rmi llm_service
