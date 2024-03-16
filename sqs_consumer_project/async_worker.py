import logging

from sqs_consumer_project.models.example_sqs_message import ExampleSQSMessageModel
from sqs_consumer_project.user_svc_client import UserSvcClient


async def do_work(message: ExampleSQSMessageModel, user_svc_client: UserSvcClient) -> bool:
    logging.info("Started work", extra={"message_name": message.name, "message_age": message.age})

    message.age += 1  # Not a higher purpose here, just mutating the data to simulate "work"
    record_user_response = await user_svc_client.record_user(message)
    if not record_user_response:
        return False

    logging.info(
        "Completed work",
        extra={"message_name": message.name, "message_age": message.age, "user_id": record_user_response.id},
    )
    return True
