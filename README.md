#XmlFeed 
--- 
To run  the project properly is necessary to also be running [Postgres](https://www.postgresql.org/), [Mongo](https://www.mongodb.com/), [Redis](https://redis.io/).

We use to development [Docker](https://www.docker.com/), [django-dotenv](https://github.com/jpadilla/django-dotenv) and others please follow the related guide to setup.

To run a local Postgres, Redis and RabbitMQ with docker, just run:
```bash
$ docker-compose up -d
```
 
Then, you can fill the `.env` file with your local setup:
```bash
$ cp .env-example .env # you can change this file if needed
```


We can run a complete setup running:
```bash
$ pipenv install
```


## Applications
xmlfeed: our main app and will have the settings file
