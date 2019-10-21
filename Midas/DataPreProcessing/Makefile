all: pull run

pull:
	docker build -t midas_preprocessing .

run:
	docker run --network=databases_default midas_preprocessing
