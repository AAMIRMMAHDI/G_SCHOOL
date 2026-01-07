# consumers.py کامل (فایل جدید در app form)
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LiveConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'live_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        # هندل SDP و candidates
        if message_type in ['offer', 'answer', 'candidate']:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_message',
                    'message': text_data_json
                }
            )

    async def webrtc_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))