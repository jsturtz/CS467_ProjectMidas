all: build run

copy_data:
	cp ../../data/* ./data/.

build:
	docker build -t data_import .

run:
	docker run --network=databases_default data_import 
