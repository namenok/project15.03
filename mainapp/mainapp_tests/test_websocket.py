from types import SimpleNamespace

import pytest
import json
import asyncio
import errno

from unittest.mock import AsyncMock, patch
from aiohttp import ClientResponseError, RequestInfo, ClientConnectorError
from channels.testing import WebsocketCommunicator
from mainapp.consumers import ChatConsumer, OllamaHttpClient
from websiteProject.asgi import application

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_chat_consumer_streaming_refactored():
    mock_ollama_http_client_instance = AsyncMock(spec=OllamaHttpClient)

    async def mock_stream_post_generator():
        yield b'{"message": {"content": "Hello"}, "done": false}\n'
        await asyncio.sleep(0.01)
        yield b'{"message": {"content": "there"}, "done": true}\n'

    mock_ollama_http_client_instance.stream_post.return_value = (
        mock_stream_post_generator()
    )

    with patch("mainapp.consumers.OllamaHttpClient") as MockOllamaHttpClientClass:
        MockOllamaHttpClientClass.return_value = mock_ollama_http_client_instance

        communicator = WebsocketCommunicator(application, "/ws/chat/")
        connected, _ = await communicator.connect()
        assert connected, "WebSocket-з'єднання не вдалося."  # nosec

        await communicator.send_to(text_data=json.dumps({"message": "hi"}))

        typing_response = await communicator.receive_from(timeout=5)
        assert "⏳" in json.loads(typing_response)["reply"], (
            "Не отримано індикатор набору тексту."
        )  # nosec

        response_1 = await communicator.receive_from(timeout=5)
        assert "Hello" in json.loads(response_1)["reply"], (
            "Не отримано фрагмент 'Hello'."
        )  # nosec

        response_2 = await communicator.receive_from(timeout=5)
        assert "there" in json.loads(response_2)["reply"], (
            "Не отримано фрагмент 'there'."
        )  # nosec

        (
            MockOllamaHttpClientClass.assert_called_once_with(),
            "Конструктор OllamaHttpClient не викликано.",
        )

        expected_system_prompt = ChatConsumer()._build_system_prompt()
        expected_messages_payload = [
            {"role": "system", "content": expected_system_prompt},
            {"role": "user", "content": "hi"},
        ]

        (
            mock_ollama_http_client_instance.stream_post.assert_called_once_with(
                endpoint="chat",
                json_payload={
                    "model": "gemma:2b",
                    "messages": expected_messages_payload,
                    "stream": True,
                },
                timeout=300,
            ),
            "Метод stream_post викликано некоректно.",
        )

        await communicator.disconnect()


@pytest.mark.asyncio
async def test_empty_message_skipped():
    communicator = WebsocketCommunicator(application, "/ws/chat/")
    connected, _ = await communicator.connect()
    assert connected, "WebSocket-з'єднання не вдалося (порожнє повідомлення)."  # nosec

    await communicator.send_to(text_data=json.dumps({"message": ""}))

    try:
        with pytest.raises(asyncio.TimeoutError):
            await communicator.receive_from(timeout=1)
    finally:
        try:
            await communicator.disconnect()
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_invalid_json_message():
    communicator = WebsocketCommunicator(application, "/ws/chat/")
    connected, _ = await communicator.connect()
    assert connected, "WebSocket-з'єднання не вдалося (невалідний JSON)."  # nosec

    await communicator.send_to(text_data="this is not json")

    error_response = await communicator.receive_from(timeout=5)
    parsed_response = json.loads(error_response)
    assert "⚠️ Невірний формат повідомлення від клієнта." in parsed_response["reply"], (
        "Не отримано очікуваного повідомлення про помилку JSON."
    )  # nosec

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_ollama_api_error_handling():
    mock_ollama_http_client_instance = AsyncMock(spec=OllamaHttpClient)

    dummy_request_info = RequestInfo(
        url="http://ollama/api/chat",
        method="POST",
        headers={},
        real_url="http://ollama/api/chat",
    )
    ollama_api_error_exception = ClientResponseError(
        request_info=dummy_request_info,
        status=500,
        message="Internal Server Error",
        headers={},
        history=(),
    )

    class ErrorRaisingAsyncIterator:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise ollama_api_error_exception

    mock_ollama_http_client_instance.stream_post.return_value = (
        ErrorRaisingAsyncIterator()
    )

    with patch("mainapp.consumers.OllamaHttpClient") as MockOllamaHttpClientClass:
        MockOllamaHttpClientClass.return_value = mock_ollama_http_client_instance

        communicator = WebsocketCommunicator(application, "/ws/chat/")
        connected, _ = await communicator.connect()
        assert connected, "WebSocket-з'єднання не вдалося (помилка API)."  # nosec

        await communicator.send_to(text_data=json.dumps({"message": "test error"}))

        typing_response = await communicator.receive_from(timeout=5)
        assert "⏳" in json.loads(typing_response)["reply"], (
            "Не отримано індикатор набору тексту перед помилкою API."
        )  # nosec

        await communicator.disconnect()


@pytest.mark.asyncio
async def test_network_error_handling():
    mock_ollama_http_client_instance = AsyncMock(spec=OllamaHttpClient)

    connection_key_mock = SimpleNamespace(
        host="localhost", port=80, is_ssl=False, ssl=None
    )

    network_error_exception = ClientConnectorError(
        os_error=OSError(errno.ECONNREFUSED, "Connection refused"),
        connection_key=connection_key_mock,
    )

    class ErrorRaisingAsyncIterator:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise network_error_exception

    mock_ollama_http_client_instance.stream_post.return_value = (
        ErrorRaisingAsyncIterator()
    )

    with patch("mainapp.consumers.OllamaHttpClient") as MockOllamaHttpClientClass:
        MockOllamaHttpClientClass.return_value = mock_ollama_http_client_instance

        communicator = WebsocketCommunicator(application, "/ws/chat/")
        connected, _ = await communicator.connect()
        assert connected, "WebSocket-з'єднання не вдалося (мережева помилка)."  # nosec

        await communicator.send_to(
            text_data=json.dumps({"message": "test network error"})
        )

        typing_response = await communicator.receive_from(timeout=5)
        assert "⏳" in json.loads(typing_response)["reply"], (
            "Не отримано індикатор набору тексту перед мережева помилкою."
        )  # nosec

        await communicator.disconnect()
