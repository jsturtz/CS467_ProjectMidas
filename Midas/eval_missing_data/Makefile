all: build run

build:
	docker build -t eval_missing_data .

run:
	docker run --network=databases_default eval_missing_data
