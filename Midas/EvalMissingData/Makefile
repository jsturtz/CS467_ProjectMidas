all: build run

build:
	docker build --build-arg proj=EvalMissingData -t midas_eval .

run:
	docker run --network=databases_default midas_eval 
