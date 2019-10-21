all: build run

build:
	docker build -t midas_run .

run:
	docker run --network=databases_default midas_run
