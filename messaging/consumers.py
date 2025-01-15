from channels.generic.websocket import AsyncWebsocketConsumer
import json
from urllib.parse import parse_qs
from .models import RealTimeMessages, AppUsers, ReadRecipient
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist


class AsyncChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles WebSocket connection. Adds the sender to their unique room group.
        """
        # Parse query parameters to get the user ID
        params_string = self.scope['query_string'].decode('utf-8')
        query_params = parse_qs(params_string)
        self.user = query_params.get('user_id', [''])[0]
        
        if not self.user:
            print("Connection rejected: Missing sender user ID")
            await self.close()
            return

        self.room_group_name = f"chat_user_{self.user}"

        print(f"User {self.user} connected. Joining room: {self.room_group_name}")
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection. Removes the sender from their room group.
        """
        print(f"User {self.user} disconnected. Leaving room: {self.room_group_name}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data):
        """
        Handles incoming WebSocket messages. Broadcasts the message to both sender and receiver.
        """
        text_data_json = json.loads(text_data)
        event_type = text_data_json.get('event', '')
        print(f"Event Type: {event_type}")

        if not event_type:
            print("Error: Missing event type in the message")
            return

        if event_type == "send_message":
            await self.handel_send_message(text_data_json)
        elif event_type == "read_receipt":
            await self.read_receipt(text_data_json)
        else:
            print(f"Unhandled event type: {event_type}")

        

    async def handel_send_message(self, text_data):
            try:
                receiver_id = text_data.get('receiver_id', '')
                message = text_data.get('message', '')
                if not receiver_id:
                    print("Error: Missing receiver_id in the message")
                    return
                print(f"Sender ID: {self.user}")
                # Create the receiver's room name
                receiver_room_name = f"chat_user_{receiver_id}"
                print(f"Message received from {self.user}: '{message}'. Sending to rooms: {receiver_room_name}, {self.room_group_name}")
                
                sender = await sync_to_async(AppUsers.objects.get)(username=self.user)
                receiver = await sync_to_async(AppUsers.objects.get)(username=receiver_id)

                print(f"Sender ID: {self.user}, Sender: {sender}")
                print(f"Receiver ID: {receiver_id}, Receiver: {receiver}")

                if receiver:
                    try:
                        # Try to create the message object
                        message_obj = await sync_to_async(RealTimeMessages.objects.create)(sender=sender, receiver=receiver, content=message, content_type="TEXT", status="SENT")

                        await sync_to_async(ReadRecipient.objects.create)(message=message_obj, recipient=receiver, status="DELIVERED")
                        print(f"Message saved with ID: {message_obj.message_id}")

                        # Send the message to both sender's and receiver's rooms
                        for room_name in [receiver_room_name, self.room_group_name]:
                            await self.channel_layer.group_send(
                                room_name,
                                {
                                    'type': 'chat_message',
                                    'message': message,
                                    'sender': self.user,
                                    'message_id': str(message_obj.message_id)
                                }
                            )

                        print(f"Message saved with ID: {message_obj.message_id}")

                    except Exception as e:
                        # If there's an error creating the message or sending it, set status as "FAILED"
                        print(f"Error: {e}. Message is not sent")
                        # Create the message object with "FAILED" status
                        await sync_to_async(RealTimeMessages.objects.create)(sender=sender, receiver=receiver, content=message, content_type="TEXT", status="FAILED")
                else:
                    print(f"Error: Receiver with ID {receiver_id} does not exist")

            except ObjectDoesNotExist as e:
                print(f"Error: User does not exist. Details: {e}")
            except json.JSONDecodeError:
                print("Error: Invalid JSON data received")
            except Exception as e:
                print(f"Error processing message: {e}")



    async def chat_message(self, event):
        """
        Handles messages sent to the WebSocket group. Updates DELIVERED status.
        """
        try:
            message = event['message']
            sender = event['sender']
            message_id = event['message_id']

            recipient_user = await sync_to_async(AppUsers.objects.get)(username=self.user)

            # Use async to fetch the query set, then perform the update with sync_to_async
            queryset = await sync_to_async(ReadRecipient.objects.filter)(
                message__message_id=message_id,
                recipient=recipient_user
            )

            # Update the status for the selected recipients
            await sync_to_async(queryset.update)(status="RECEIVED")

            # Send the message to the WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
                'sender': sender,
                'message_id':message_id
            }))
        except Exception as e:
            print(f"Error delivering message: {e}")


    async def read_receipt(self, text_data_json):
        """
        Updates READ status when the recipient marks a message as read.
        """
        try:
            print("This is already in JSON")
            message_id = text_data_json.get('message_id', '')

            if not message_id:
                print("Error: Missing message_id in the read receipt")
                return

            recipient_user = await sync_to_async(AppUsers.objects.get)(username=self.user)
            updated_rows = await sync_to_async(ReadRecipient.objects.filter)(
                message__message_id=message_id,
                recipient=recipient_user
            )

            await sync_to_async(updated_rows.update)(status="READ")
            print(f"Message {message_id} marked as READ by {self.user}")

        except ObjectDoesNotExist as e:
            print(f"Error: Message or User does not exist. Details: {e}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON data received")
        except Exception as e:
            print(f"Error processing read receipt: {e}")
