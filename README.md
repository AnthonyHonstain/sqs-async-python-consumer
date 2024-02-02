# Overview
This is a toy SQS consumer written in python, its purpose it to help explore different async options and try different 
concurrency scenarios (messages with fast vs slow processing times).

If you wanted to deploy this somewhere, you would need to extract urls and related configuration. I only ever took this
as far as local development.

Using localstack SQS for the queue and wiremock for the consumer to execute an HTTP call against.

The automated tests are very basic, verifies basic SQS 

# Local Development - Guide

* Requirements (guide for using Mamba to install python and poetry later in the README in section "Mamba guide for python+poetry dependencies")
  * Python 3.12 https://www.python.org/downloads/release/python-3120/
  * Poetry https://python-poetry.org/
  * Docker for running localstack and wiremock https://docs.docker.com/compose/
* Install dependencies: `poetry install`
* Format code: `black .`
* Run automated tests: `poetry run pytest`
* Start the service: `poetry run python sqs_consumer_project/sqs_consumer.py`

# Important Commands

Docker compose should be able to standup wiremock and localstack with the initial required configuration.
* Wiremock - with a basic (and delayed) response
* localstack - with the queue setup you need for testing (which is done via the `init-localstack.sh` script that runs as part of docker compose).

## Manual commands
```
# List the queues
aws --endpoint-url=http://localhost:4566 sqs list-queues

# Create a queue
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name my-queue2 --region us-east-1

# Run the service
poetry run python sqs_consumer_project/sqs_consumer.py

# Send a message
aws --endpoint-url=http://localhost:4566 sqs send-message --queue-url http://localhost:4566/000000000000/my-queue2 --message-body '{"name": "Anthony", "age":2, "ignored":"new-fields"}'

# Get queue attributes
aws --endpoint-url=http://localhost:4566 sqs get-queue-attributes --queue-url http://localhost:4566/000000000000/my-queue2 --attribute-names All

# Purge Queue
aws --endpoint-url=http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/test-my-queue2
```

# Mamba guide for python+poetry dependencies
These are the exact steps I used on a Ubuntu 23.10 install.

There are many other ways to do this, this is still the best route I have found for dealing with multiple python versions and
having a smooth integration with IntelliJ (ymmv).

```
mamba create -n sqs-async-consumer -c conda-forge  python=3.12

mamba activate sqs-async-consumer

pip install poetry
    ❯ poetry -V     
    Poetry (version 1.7.1)

poetry env info         

poetry install

poetry config --list
```