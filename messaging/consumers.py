from channels.generic.websocket import AsyncWebsocketConsumer
import json
from urllib.parse import parse_qs

class AsyncChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        params_string = self.scope['query_string'].decode('utf-8')
        query_params = parse_qs(params_string)
        self.sender = query_params.get('user_id', [''])[0]  # Get sender user ID
        
        if not self.sender:
            await self.close()
            return
        
        # Create sender's room name
        self.room_name = f"user_{self.sender}"
        self.room_group_name = f"chat_{self.room_name}"

        # Join the sender's room
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
        message = text_data_json['message']
        receiver_id = text_data_json.get('receiver_id', '')

        # Create receiver's room name
        receiver_room_name = f"chat_user_{receiver_id}"

        # Send the message to the receiver's room and sender's room
        for room_name in [receiver_room_name, self.room_group_name]:
            await self.channel_layer.group_send(
                room_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.sender  # Include sender's user ID
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))
