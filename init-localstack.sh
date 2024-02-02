#!/bin/bash

# Wait for LocalStack to be ready
echo "Waiting for LocalStack to be ready..."
until aws --region us-east-1 --endpoint-url=http://localstack:4566 sqs list-queues; do
  echo "Waiting for LocalStack SQS to be ready..."
  sleep 1
done

# Create an SQS queue
echo "Creating an SQS queue..."
aws --endpoint-url=http://localstack:4566 sqs --region us-east-1 create-queue --queue-name my-queue2

echo "LocalStack initialization completed."
