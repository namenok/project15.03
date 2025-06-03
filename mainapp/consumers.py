
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import aiohttp

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')

        if not message:
            await self.send(text_data=json.dumps({'error': 'Empty message'}))
            return

        response_text = await self.query_ollama("http://localhost:11434/api/generate", {"prompt": message})

        await self.send(text_data=json.dumps({'reply': response_text}))

    async def query_ollama(self, url, payload):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                full_response = ""
                async for line in resp.content:
                    data = json.loads(line.decode())
                    full_response += data.get("response", "")
                    if data.get("done"):
                        break
                return full_response
