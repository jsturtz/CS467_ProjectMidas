all: build run

build:
	docker build -t run_model

run:
	docker run --network=databases_default run_model
