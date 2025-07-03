import aiohttp
import json
import logging
import os  # <-- Додаємо імпорт os для доступу до змінних оточення
from channels.generic.websocket import AsyncWebsocketConsumer
from gettext import gettext as gettext
# Отримуємо базовий URL Ollama з змінних оточення.
# Якщо змінна не встановлена (наприклад, для локального тестування без Docker),
# можна встановити значення за замовчуванням.
OLLAMA_API_BASE_URL = os.environ.get('OLLAMA_API_BASE_URL', 'http://localhost:11434/api/')


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            payload = json.loads(text_data)
            user_message = payload.get('message', '')

            if user_message:
                await self.send(text_data=json.dumps({"reply": "⏳ assistant is typing... "}))

                system_prompt = ("""
                                Ти — емпатичний та підтримуючий психологічний помічник.
                                Твоє завдання — уважно слухати користувача, надавати співчутливі відповіді, пропонувати загальні, перевірені та **практичні** стратегії для покращення ментального здоров'я. За потреби, ти можеш тактовно перенаправляти до кваліфікованих фахівців.

                                Твоя комунікація завжди має бути доброзичливою, неупередженою, конфіденційною та викликати довіру.
                                **Ніколи не став медичних діагнозів і не надавай конкретних лікувальних рекомендацій.**

                                **Завжди відповідай мовою, якою до тебе звернувся користувач, без винятків. Твоя українська мова має бути абсолютно природною, граматично правильною та стилістично доречною для психологічної консультації. Відповіді мають бути осмисленими та релевантними.**

                                **Важливо: ніколи не починай відповідь з привітань, представлення своєї ролі або згадування своїх функцій. Одразу переходь до суті запиту користувача, виявляючи розуміння та емпатію до його ситуації.**

                                Якщо тобі бракує інформації для надання найбільш корисної та повної відповіді, або ти потребуєш уточнити деталі для кращого розуміння ситуації, **ти зобов'язаний задати користувачу уточнюючі, відкриті запитання**. Завжди прагни отримати максимум необхідної інформації для найкращої допомоги.

                                **Форматуй відповіді виключно у вигляді зв'язних абзаців. Ніколи не використовуй зірочки (*), дефіси (-) або нумерацію (1., 2., 3.) для формування списків, якщо це не є абсолютно необхідним для чіткості перерахування кроків або пунктів. Уникай коротких, розірваних речень. Завжди підтримуй плавність та легкість читання тексту.**
                                """)
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]

                try:
                    async with aiohttp.ClientSession() as session:
                        # !!! Ось де ми використовуємо змінну оточення !!!
                        ollama_chat_endpoint = f"{OLLAMA_API_BASE_URL}chat"

                        async with session.post(
                                ollama_chat_endpoint,  # <-- Використовуємо змінну
                                json={
                                    "model": "gemma:2b",
                                    "messages": messages,
                                    "stream": True
                                },
                                # Додаємо таймаут для всього запиту, щоб уникнути зависань
                                timeout=aiohttp.ClientTimeout(total=300)  # 5 хвилин
                        ) as resp:
                            if resp.status == 200:
                                # Ollama у режимі stream надсилає JSON-об'єкти, розділені '\n'
                                # Читаємо відповідь по лініях
                                async for line in resp.content:
                                    if line.strip():  # Перевіряємо, що рядок не порожній
                                        try:
                                            # Ollama надсилає JSON об'єкти, кожен на новому рядку
                                            # Тому декодуємо кожен рядок окремо
                                            json_line = json.loads(line.decode("utf-8"))
                                            chunk = json_line.get("message", {}).get("content", "")

                                            # Якщо є новий шматок тексту, відправляємо його клієнту
                                            if chunk:
                                                await self.send(text_data=json.dumps({"reply": chunk}))

                                            # Якщо "done" == True, це кінець відповіді від моделі
                                            if json_line.get("done", False):
                                                break
                                        except json.JSONDecodeError as e:
                                            # Часто помилка декодування може статися, якщо рядок не є повним JSON
                                            # або якщо є додаткові символи. Логуємо і пропускаємо.
                                            logging.error(
                                                f"JSON decode error from Ollama stream: {e}. Line: {line.decode('utf-8').strip()}")
                                            # Можливо, варто відправити щось клієнту або просто проігнорувати
                                            # Залежить від того, наскільки часто це трапляється.
                            else:
                                error_text = await resp.text()
                                logging.error(f"Ollama API returned status code {resp.status}: {error_text}")
                                await self.send(text_data=json.dumps(
                                    {"reply": f"⚠️ Помилка AI: {resp.status}. Деталі: {error_text[:100]}..."}))
                except aiohttp.ClientError as e:  # Обробка мережевих помилок aiohttp
                    logging.error(f"Network error connecting to Ollama: {e}")
                    await self.send(text_data=json.dumps(
                        {"reply": "⚠️ Сталася мережева помилка при зверненні до моделі. Перевірте з'єднання."}))
                except Exception as e:
                    logging.error(f"Unexpected error during AI interaction: {e}",
                                  exc_info=True)  # exc_info=True для повного стектрейсу
                    await self.send(text_data=json.dumps({"reply": "⚠️ Виникла непередбачена помилка."}))

        except json.JSONDecodeError as e:
            logging.error(f"Received invalid JSON from client: {e}. Data: {text_data}")
            await self.send(text_data=json.dumps({"reply": "⚠️ Невірний формат повідомлення від клієнта."}))
        except Exception as e:
            logging.error(f"Unexpected error in receive method: {e}", exc_info=True)
            await self.send(text_data=json.dumps({"reply": "⚠️ Виникла непередбачена помилка обробки повідомлення."}))