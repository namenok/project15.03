import aiohttp
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Додаткові налаштування для підключення

    async def receive(self, text_data):
        try:
            payload = json.loads(text_data)
            user_message = payload.get('message', '')

            if user_message:
                await self.send(text_data=json.dumps({"reply": "⏳ Обробляємо ваше повідомлення..."}))

                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            "http://host.docker.internal:11434/api/chat",
                            json={
                                "model": "llama3.1",
                                "messages": [{"role": "user", "content": user_message}],
                                "stream": True
                            }
                        ) as resp:
                            if resp.status == 200:
                                async for line in resp.content:
                                    if line:
                                        try:
                                            json_line = json.loads(line.decode("utf-8"))
                                            chunk = json_line.get("message", {}).get("content", "")
                                            if chunk:
                                                await self.send(text_data=json.dumps({"reply": chunk}))
                                            if json_line.get("done", False):
                                                break
                                        except json.JSONDecodeError as e:
                                            logging.error(f"JSON decode error: {e}")
                            else:
                                logging.error(f"API returned status code {resp.status}")
                except Exception as e:
                    logging.error(f"Stream error: {e}")
                    await self.send(text_data=json.dumps({"reply": "⚠️ Сталася помилка при зверненні до моделі."}))

        except json.JSONDecodeError as e:
            logging.error(f"Received invalid JSON: {e}")
            await self.send(text_data=json.dumps({"reply": "⚠️ Невірний формат повідомлення."}))
