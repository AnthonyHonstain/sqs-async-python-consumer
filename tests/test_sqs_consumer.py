import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from aiobotocore.session import get_session

from sqs_consumer_project.models.example_sqs_message import ExampleSQSMessageModel
from sqs_consumer_project.sqs_consumer import consume_messages, message_processor
from sqs_consumer_project.user_svc_client import UserSvcClient

QUEUE_NAME = "test-my-queue2"
client_instance = UserSvcClient("http://localhost:8080")


@pytest.mark.asyncio
@patch("sqs_consumer_project.sqs_consumer.do_work", new_callable=AsyncMock)
async def test_sqs_consumer(mock_do_work):
    shutdown_signal = asyncio.Event()

    async with get_session().create_client(
        "sqs",
        region_name="us-east-1",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    ) as sqs_client:
        # Create the queue
        await sqs_client.create_queue(QueueName=QUEUE_NAME)

        # Send a message
        test_message = '{"name": "Anthony", "age":2, "unknown":"unknown-fields"}'
        await sqs_client.send_message(QueueUrl=QUEUE_NAME, MessageBody=test_message)
        mock_do_work.return_value = True

        # Start the consumer in a background task
        consumer_task = asyncio.create_task(consume_messages(QUEUE_NAME, shutdown_signal, client_instance))

        # Wait a bit to ensure the message is processed
        await asyncio.sleep(0.25)  # Adjust the sleep time as needed

        # Signal the consumer to shut down
        shutdown_signal.set()

        # Wait for the consumer to finish
        await consumer_task

        mock_do_work.assert_called_once()
        mock_do_work.assert_called_with(ExampleSQSMessageModel(name="Anthony", age=2), client_instance)


@pytest.mark.asyncio
@patch("sqs_consumer_project.sqs_consumer.do_work", new_callable=AsyncMock)
async def test_message_processor__successful_deserialization(mock_do_work):
    mock_do_work.return_value = True
    result = await message_processor("1234", '{"name": "Anthony", "age":2}', client_instance)
    assert result is True
    mock_do_work.assert_called_once()
    mock_do_work.assert_called_with(ExampleSQSMessageModel(name="Anthony", age=2), client_instance)


@pytest.mark.asyncio
@patch("sqs_consumer_project.sqs_consumer.do_work", new_callable=AsyncMock)
async def test_message_processor__error_deserialization(mock_do_work):
    mock_do_work.return_value = True
    message_body = '{"name": "Anthony"}'  # This is missing a required field
    result = await message_processor("1234", message_body, client_instance)
    assert result is False
    mock_do_work.assert_not_called()


@pytest.mark.asyncio
@patch("sqs_consumer_project.sqs_consumer.do_work", new_callable=AsyncMock)
async def test_message_processor__wrong_types_deserialization(mock_do_work):
    mock_do_work.return_value = True
    message_body = '{"name": 2, "age": "ABC"}'  # This has the wrong types for "name" and "age" fields
    result = await message_processor("1234", message_body, client_instance)
    assert result is False
    mock_do_work.assert_not_called()
