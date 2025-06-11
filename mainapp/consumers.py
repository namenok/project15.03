import aiohttp
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Просто приймаємо з'єднання
        await self.accept()

    async def disconnect(self, close_code):
        # Тут нічого не потрібно, бо ми не підписані на групи
        pass

    async def receive(self, text_data):
        try:
            payload = json.loads(text_data)
            user_message = payload.get('message', '')

            if user_message:
                await self.send(text_data=json.dumps({"reply": "⏳ assistant is typing... "}))
                #  системний промпт
                system_prompt = """
                                Ти - емпатичний психологічний помічник, який спеціалізується на підтримці користувачів українською та англійською мовами.
                                Твоє завдання - уважно слухати, надавати співчутливі відповіді, пропонувати загальні стратегії для покращення ментального здоров'я та, за потреби, перенаправляти до фахівців.
                                Ніколи не надавай медичних діагнозів чи конкретних лікувальних рекомендацій.
                                Будь завжди доброзичливим, неупередженим та конфіденційним.
                                """
                # Створіть список повідомлень, включаючи системний промпт
                # Системний промпт завжди йде першим у списку messages
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]

                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            "http://host.docker.internal:11434/api/chat",
                            json={
                                "model": "gemma:2b",
                                "messages": messages,
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
                                logging.error(f"API returned status code {resp.status}: {await resp.text()}")
                except Exception as e:
                    logging.error(f"Stream error: {e}")
                    await self.send(text_data=json.dumps({"reply": "⚠️ Сталася помилка при зверненні до моделі."}))

        except json.JSONDecodeError as e:
            logging.error(f"Received invalid JSON: {e}")
            await self.send(text_data=json.dumps({"reply": "⚠️ Невірний формат повідомлення."}))
