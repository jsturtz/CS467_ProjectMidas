all: build run

copy_data:
	cp ../../data/* ./data/.

build:
	docker build -t midas_import .

run:
	docker run midas_import
