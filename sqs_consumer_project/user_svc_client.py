import httpx
from httpx import HTTPError, URL
import logging

from pydantic import ValidationError

from sqs_consumer_project.models.example_sqs_message import ExampleSQSMessageModel
from sqs_consumer_project.models.record_user_response import RecordUserResponse


class UserSvcClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.record_user_path = "/record_user"

    async def record_user(self, message: ExampleSQSMessageModel) -> RecordUserResponse | None:
        # TODO - This is not initially intended to be optimized, just yanked the HTTP call code out to its
        #  own place so we can experiment/iterate on different configurations of setup (connection pooling) and testing.
        async with httpx.AsyncClient() as client:
            json_body = message.model_dump_json()

            try:
                response = await client.post(URL(self.base_url).join(self.record_user_path), json=json_body)
                response.raise_for_status()
            except HTTPError as exc:
                logging.error("Failed with HTTP error", extra={"error": exc})
                return

            try:
                record_user_response = RecordUserResponse(**response.json())
                logging.info("Received response", extra={"user_id": record_user_response.user_id})
            except ValidationError as e:
                logging.error("Failed to deserialize response", extra={"error": e})
                return
        return record_user_response
