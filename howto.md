# A How-To guide to Project Midas

## Precursor
In this zipped directory, there should be files under CS467_ProjectMidas/datastores/csv called train_transaction.csv, train_transaction_2K.csv, and train_trasaction_40K.csv.zip. These are all datafiles (after unzipping train_trasaction_40K.csv.zip) that can be used to train a machine learning model. To do so, either load the project locally (not recommended) or access the hosted web version at http://ec2-18-219-155-220.us-east-2.compute.amazonaws.com/.


## Installation (if not using the hosted web version)
To bring up the local version, an updated version of docker will be required. Please select and install the version appropriate to your machine, found at https://docs.docker.com/v17.09/engine/installation/#server.

After docker has been installed, please check that docker is running on your local machine. You can do this by opening a terminal and typing `docker ps`. This should provide an output that indicates what docker instances are currently running on your local machine.

In your terminal, navigate to the project home directory. In this directory, there should be a file called "docker-compose.yml". In your terminal, type `docker-compose build`. This will initiate a process that will build the containerized application on your machine. This may take a while. The following text indicates completion:

```
Successfully built <version_hex_goes_here, ex: c4708d04c857>
Successfully tagged cs467_projectmidas_web:latest
```

After the container has been built, run `docker-compose up` in your terminal. This will start the mongo, postgres, and application containers. The following text indicates that the application (and postgres server) is up and running:

```
web_1       | Django version 2.2.6, using settings 'MidasWebsite.settings'
web_1       | Starting development server at http://0.0.0.0:8000/
web_1       | Quit the server with CONTROL-C.
```

The following text indicates that the mongo container is up and running:
```
mongo_1     | 2019-12-05T04:42:06.254+0000 I  NETWORK  [initandlisten] Listening on /tmp/mongodb-27017.sock
mongo_1     | 2019-12-05T04:42:06.254+0000 I  NETWORK  [initandlisten] Listening on 0.0.0.0
```

If these messages are not sent to your console, please send a SIGINT (ctrl-c for most terminals) to the terminal and try again. Upon receiving the signal, the console should output the following:

```
Stopping cs467_projectmidas_web_1      ... done
Stopping cs467_projectmidas_mongo_1    ... done
Stopping cs467_projectmidas_postgres_1 ... done
```

Once the application and mongo are up and running, use a web browser and navigate to 0.0.0.0/.

## 