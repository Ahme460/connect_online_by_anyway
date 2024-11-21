from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async

from chat.utils import generate_chat_name
from .models import Message, Customer_user, Chat_name
from django.utils import timezone



class BaseConsumer(AsyncWebsocketConsumer):
    async def __call__(self, scope, receive, send):
        self.user:Customer_user = scope['user']
        self.headers:dict = scope['headers']
        self.query_string:dict[str,list] = scope['query_string']
        return await super().__call__(scope, receive, send)


class MyConsumer(BaseConsumer):

    async def connect(self):
        if not self.user:
            await self.close()
        else:
            await self.accept()
            self.chat_id = generate_chat_name(self.user.id , self.query_string['recevier'][0]) 

            self.user.status = True
            await self.update_message_status('connect')
            await database_sync_to_async(self.user.save)()

            await self.channel_layer.group_add(
                self.chat_id,
                self.channel_name
            )
            await self.channel_layer.group_send(
                self.chat_id,
                {
                    "type": "online",
                }
            )

    async def online(self, event):
        await self.send(
            text_data=json.dumps({
                "status": "online",
            })
        )


    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        receiver_id = self.query_string['recevier'][0]
        receiver_status = await self.get_user_status(int(receiver_id))
        message_type = 'connect' if receiver_status else 'disconnect'
        await self.channel_layer.group_send(
            generate_chat_name(self.user.id,receiver_id),
            {
                "type": "chat_message",
                "message": message,
                "sender": self.user.id,
                "receiver": receiver_id
            }
        )

    async def disconnect(self, close_code):
        chat_ids = await self.get_users_app()
        self.user.status = False
        self.user.last_seen = timezone.now()
        await database_sync_to_async(self.user.save)()

        for chat_id in chat_ids:
            chat_name = f'chat_{int(self.user.id) + int(chat_id)}'
            await self.channel_layer.group_discard(
                chat_name,
                self.channel_name
            )
            await self.channel_layer.group_send(
                chat_name,
                {
                    'type': 'send_dis',
                    'user_id': self.user.id
                }
            )

    async def send_dis(self, event):
        user_id = event['user_id']
        await self.send(
            text_data=json.dumps({
                'status': 'offline',
                'last_seen': str(timezone.now()),
                'user_id': user_id,
                'users_online': list(self.online_users)
            })
        )
        

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']
        await self.send(
            text_data=json.dumps({
                'message': message,
                'sender': sender,
                'receiver': receiver
            })
        )
        
        
        
        

    @database_sync_to_async
    def save_message(self, chat_id, sender, receiver, message, type_message):
        sender_user = Customer_user.objects.get(id=sender)
        receiver_user = Customer_user.objects.get(id=receiver)
        chat_name , created = Chat_name.objects.get_or_create(name=chat_id,user_1=sender_user,user_2=receiver_user)
        
        return Message.objects.create(
            message=message,
            timestamp=timezone.now(),
            type_message=type_message,
            chat_name=chat_name,
            sender=sender_user,
            receiver=receiver_user
            
        )
    @database_sync_to_async
    def get_online_user(self):
        return list(Customer_user.objects.filter(status=True).exclude(id=self.user.id).values_list('id', flat=True))


    @database_sync_to_async
    def update_message_status(self, status):
        Message.objects.filter(receiver=self.user).update(type_message=status)

    @database_sync_to_async
    def get_users_app(self):
        return list(Customer_user.objects.exclude(id=self.user.id).values_list('id', flat=True))

    
    @database_sync_to_async
    def get_user_status(self, user_id):
        return Customer_user.objects.get(id=user_id).status
    
    
#daphne -p 8000 project.asgi:application
