DIR := ${CURDIR}

all: run

run:
	mkdir -p ${DIR}/datastores/mongo
	mkdir -p ${DIR}/datastores/postgres
	docker-compose up -d

down:
	docker-compose down
	docker-compose rm -f

remove_files:
	rm -rf ${DIR}/datastores/mongo
	rm -rf ${DIR}/datastores/postgres

clean: down remove_files
