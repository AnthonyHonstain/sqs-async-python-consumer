import asyncio
import json
import sys
import logging

import botocore.exceptions
import pydantic
from aiobotocore.session import get_session

from sqs_consumer_project.async_worker import do_work
from sqs_consumer_project.models.example_sqs_message import ExampleSQSMessageModel
from sqs_consumer_project.setup import setup_logging
from sqs_consumer_project.user_svc_client import UserSvcClient


async def consume_messages(queue_name: str, shutdown_signal: asyncio.Event, user_svc_client: UserSvcClient):
    async with get_session().create_client(
        "sqs",
        region_name="us-east-1",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    ) as client:
        try:
            get_url_response = await client.get_queue_url(QueueName=queue_name)
        except botocore.exceptions.ClientError as err:
            if err.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
                logging.error(f"Queue {queue_name} does not exist")
                sys.exit(1)
            else:
                raise

        queue_url = get_url_response["QueueUrl"]

        while not shutdown_signal.is_set():
            logging.info("Polling for messages")
            try:
                receive_message_response = await client.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=2,
                )

                if "Messages" in receive_message_response:
                    logging.info(
                        "receive_messages got messages",
                        extra={"message_count": len(receive_message_response["Messages"])},
                    )
                    for msg in receive_message_response["Messages"]:
                        message_id = msg["MessageId"]
                        message_body = msg["Body"]
                        successfully_processed = await message_processor(message_id, message_body, user_svc_client)

                        if successfully_processed:
                            # Need to remove msg from queue or else it'll reappear, you could see this by
                            # checking ApproximateNumberOfMessages and ApproximateNumberOfMessagesNotVisible
                            # in the queue.
                            await client.delete_message(
                                QueueUrl=queue_url,
                                ReceiptHandle=msg["ReceiptHandle"],
                            )
                        else:
                            logging.error("Failed to process message", extra={"message_id": message_id})
                else:
                    logging.debug("No messages in queue")
            except asyncio.CancelledError:
                logging.error("Cancel Error")
                break

        logging.info("Finished")


async def message_processor(message_id: str, message_body: str, user_svc_client: UserSvcClient) -> bool:
    logging.info("Starting MessageId processing", extra={"message_id": message_id})
    try:
        message_dict = json.loads(message_body)
        message = ExampleSQSMessageModel.model_validate(message_dict)
        logging.info("pydantic model", extra={"sqs_message": message})
    except pydantic.ValidationError as e:
        logging.error("Invalid message format", extra={"error": e})
        return False

    return await do_work(message, user_svc_client)


async def main():
    setup_logging()

    user_svc_base_url = "http://localhost:8080"
    user_svc_client = UserSvcClient(user_svc_base_url)
    queue_name = "my-queue2"
    consumer_count = 2
    shutdown_signal = asyncio.Event()
    consumers = [consume_messages(queue_name, shutdown_signal, user_svc_client) for _ in range(consumer_count)]
    await asyncio.gather(*consumers)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Script interrupted by user")
