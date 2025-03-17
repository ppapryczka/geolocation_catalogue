# geolocation_catalogue
Geolocation catalogue - FastAPI application with Postgresql backend which stores geolocation info of IP addresses and hostnames.

## Running application
Project uses poetry as dependency manager. Here you can find information how to install poetry: https://python-poetry.org/docs/#installation.

After getting poetry execute following commands:
```
poetry install
eval $(poetry env activate)
```
After that you will have all dependencies installed and environment activated.

You need to set environmentvariable called **pg_dsn**. It descries PostgreSQL DSN address used as a backend, example value: `postgresql://user:mysecretpassword@localhost:5432/postgres`.

Additionally, you can set environment variable called **ip_stack_api_access_key**, which holds the value of your IPStack(`https://ipstack.com/`) API access key. If you set your key, when you call the GET endpoint and there is no database record for the provided address, IPStack will be called internally. If the call is successful, a new record will be created in the database.

After setting environment variables you can run application by calling:
```
sh ./start.sh
```

In second terminal you can provide some test data by executing:
```
sh ./put_test_data.sh
```
From now application is running at port 8000.

To interact with API you can open address `http://localhost:8000/docs` on your browser.

## Tests
To execute tests you have to run local database. It is recommended to run it via provided docker by executing:
```
docker compose -f docker-compose-tests.yml  up
```

In second terminal you can run tests by calling following commands:
```
eval $(poetry env activate)
pytest
```

## Running via docker
There is also option to run application via docker-compose. For such approach execute:
```
docker compose up  --build
```
From now application is running at port 8000 and PostgreSQL is running at port 5432.


In second terminal you can provide some test data by executing:
```
sh ./put_test_data.sh
```
