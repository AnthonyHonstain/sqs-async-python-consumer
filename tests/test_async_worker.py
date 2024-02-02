import pytest
import respx
from httpx import Response

from sqs_consumer_project.async_worker import do_work
from sqs_consumer_project.models.example_sqs_message import ExampleSQSMessageModel
from sqs_consumer_project.user_svc_client import UserSvcClient


@pytest.mark.asyncio
@respx.mock
async def test_do_work__successful_post():
    url = "http://localhost:8080/record_user"
    expected_content = b'"{\\"name\\":\\"Test Name\\",\\"age\\":21}"'

    post_route = respx.post(url).mock(return_value=Response(200, json={"user_id": "123"}))

    test_message = ExampleSQSMessageModel(name="Test Name", age=20)

    result = await do_work(test_message, UserSvcClient("http://localhost:8080"))
    assert result is True

    assert post_route.called
    assert post_route.call_count == 1
    assert post_route.calls.last.request.content == expected_content


@pytest.mark.asyncio
@respx.mock
async def test_do_work__failed_post():
    url = "http://localhost:8080/record_user"
    respx.post(url).mock(return_value=Response(500, json={"user_id": "123"}))

    test_message = ExampleSQSMessageModel(name="Test Name", age=20)

    result = await do_work(test_message, UserSvcClient("http://localhost:8080"))
    assert result is False


@pytest.mark.asyncio
@respx.mock
async def test_do_work__expected_post_result():
    url = "http://localhost:8080/record_user"
    respx.post(url).mock(return_value=Response(200, json={"UNKNOWN": "UNEXPECTED_RESPONSE"}))

    test_message = ExampleSQSMessageModel(name="Test Name", age=20)

    result = await do_work(test_message, UserSvcClient("http://localhost:8080"))
    assert result is False
