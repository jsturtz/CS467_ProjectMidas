## Start DBs
`make run`

## Cleanup Docker Containers
`make down`

Note: this won't remove the files on your local machine

## Remove Everything
`make clean`

Note: This will take down the database docker containers and the files. Running `make run` again will start you with completely empty instances of postgres and mongo.

## Data Storage Locations (local)
./datastores/mongo
./datastores/postgres
