## Install & Run in Local Environment

### Setup Python Environment

This system requires Python (version >= `3.10`). Use the following command to install the dependencies.

```shell
pip install -r requirements.txt
```

### Setup MySQL Server

This system requires an MySQL instance (version >= `5.3`). When MySQL is ready, please use the `mysql` client command
and [docs/scripts/create_table.sql](docs/scripts/create_table.sql) to initialize the database, *e.g.*

```bash
mysql < docs/scripts/create_table.sql
```

### Setup OpenSearch

This system requires an OpenSearch instance (version >= `2.11`). Please refer
to [OpenSearch Quickstart](https://opensearch.org/docs/latest/quickstart/) for installation instructions.

### Update Configurations

You must update some configurations in [src/dms/config/dev_config.py](src/dms/config/prod_config.py) before running the
server.

1. Update `SECRET_KEY` to a random long string
   for [singing the cookies](https://flask.palletsprojects.com/en/3.0.x/config/#SECRET_KEY);
2. Update `SQLALCHEMY_DATABASE_URI` according to the actual setup of the MySQL instance;
3. Update `OPENSEARCH_HOST`, `OPENSEARCH_PORT`, `OPENSEARCH_USER` and `OPENSEARCH_PASSWORD` according to the actual
   setup of the OpenSearch instance.

**Note:** In [src/dms/app.py](src/dms/app.py), the global variable `DEFAULT_ENV` is `prod`. If you change it to `dev`,
please update the above configurations in `src/dms/config/dev_config.py` instead.

### Run Locally

You can run the server with the following command.

```bash
python manager.py runserver
```
