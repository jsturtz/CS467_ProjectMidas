all: pull run

pull:
	docker build -t data_preprocessing .

run:
	docker run --network=databases_default data_preprocessing
