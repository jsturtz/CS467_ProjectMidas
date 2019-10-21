all: build run

build:
	docker build -t midas_eval .

run:
	docker run --network=databases_default midas_eval 
