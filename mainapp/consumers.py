import aiohttp
import json
import logging
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from langdetect import detect, LangDetectException

OLLAMA_API_BASE_URL = os.environ.get(
    "OLLAMA_API_BASE_URL", "http://localhost:11434/api/"
)


class HttpClient:
    async def stream_post(self, url: str, json_payload: dict, timeout: int):
        raise NotImplementedError(
            "stream_post method must be implemented by subclasses"
        )


class OllamaHttpClient(HttpClient):
    def __init__(self, base_url: str = OLLAMA_API_BASE_URL):
        self.base_url = base_url

    async def stream_post(self, endpoint: str, json_payload: dict, timeout: int):
        full_url = f"{self.base_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    full_url,
                    json=json_payload,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as resp:
                    resp.raise_for_status()
                    async for chunk in resp.content:
                        yield chunk
            except aiohttp.ClientError as e:
                raise e


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_client = kwargs.get("http_client", OllamaHttpClient())

    async def connect(self):
        await self.accept()
        logging.info("WebSocket connected.")

    async def disconnect(self, close_code):
        logging.info(f"WebSocket disconnected with code: {close_code}")
        pass

    async def receive(self, text_data):
        try:
            payload = json.loads(text_data)
            user_message = payload.get("message", "")
            if not user_message:
                logging.warning("Received empty message from client.")
                return

            await self.send(
                text_data=json.dumps({"reply": "⏳ assistant is typing..."})
            )

            messages = self._build_ollama_messages(user_message)

            await self._stream_ollama_response(messages)

        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON from client: {e}. Data: {text_data}")
            await self._send_error("⚠️ Невірний формат повідомлення від клієнта.")
        except aiohttp.ClientResponseError as e:
            logging.error(
                f"Ollama API error {e.status}: {e.message}. URL: {e.request_info.url}"
            )
            await self._send_error(
                f"⚠️ Помилка AI: {e.status}. Деталі: {e.message[:100]}..."
            )
        except aiohttp.ClientError as e:
            logging.error(f"Network error during Ollama API call: {e}", exc_info=True)
            await self._send_error(
                "⚠️ Сталася мережева помилка при зверненні до моделі. Перевірте з'єднання."
            )
        except Exception as e:
            logging.error(
                f"Unexpected error during message processing: {e}", exc_info=True
            )
            await self._send_error(
                "⚠️ Виникла непередбачена помилка обробки повідомлення."
            )

    def _build_system_prompt(self, lang_hint: str = "") -> str:
        hint_line = ""
        if lang_hint == "uk":
            hint_line = "\nКористувач розмовляє українською. ВІДПОВІДАЙТЕ ТІЛЬКИ УКРАЇНСЬКОЮ. НЕ додавайте переклад на англійську. Не використовуйте англійську мову взагалі."
        elif lang_hint == "en":
            hint_line = "\nThe user is speaking English. Respond ONLY in English. DO NOT translate to any other language."
        else:
            hint_line = "\nThe language is unknown. Use Ukrainian only. DO NOT translate."

        return f"""
            You are a polite and empathetic psychologist helping users online.
            Your task is to reply in the exact same language the user used.
            DO NOT translate or repeat the message in any other language.
            NEVER use more than one language in your response.
            Your tone should be kind, respectful, and supportive.
            Speak clearly and simply.

            Ви — емпатичний психолог. ВІДПОВІДАЙТЕ ТІЛЬКИ тією ж мовою, що й користувач.
            НІКОЛИ не перекладайте і не використовуйте другу мову в одній відповіді.
            Ваша відповідь має бути ЛИШЕ українською, якщо користувач говорить українською.

            {hint_line}
        """

    def _build_ollama_messages(self, user_message: str):
        try:
            detected_lang = detect(user_message)
        except LangDetectException:
            detected_lang = ""

        if detected_lang.startswith("uk"):
            lang_hint = "uk"
        elif detected_lang.startswith("en"):
            lang_hint = "en"
        else:
            lang_hint = "fallback"

        return [
            {"role": "system", "content": self._build_system_prompt(lang_hint)},
            {"role": "user", "content": user_message},
        ]

    async def _stream_ollama_response(self, messages):
        async for line_bytes in self.http_client.stream_post(
            endpoint="chat",
            json_payload={"model": "gemma3:1b", "messages": messages, "stream": True},
            timeout=300,
        ):
            if line_bytes.strip():
                try:
                    json_line = json.loads(line_bytes.decode("utf-8"))
                    chunk = json_line.get("message", {}).get("content", "")
                    if chunk:
                        await self.send(text_data=json.dumps({"reply": chunk}))
                    if json_line.get("done", False):
                        break
                except json.JSONDecodeError as e:
                    logging.error(
                        f"Stream decode error: {e}. Line: {line_bytes.decode('utf-8', errors='ignore')}"
                    )
            else:
                logging.debug("Received empty line from stream.")

    async def _send_error(self, message: str):
        await self.send(text_data=json.dumps({"reply": message}))
