all: build run

build:
	docker build -t train_model

run:
	docker run --network=databases_default train_model
