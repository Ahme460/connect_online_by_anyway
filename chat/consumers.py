from channels.generic.websocket import AsyncWebsocketConsumer
import json
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from .models import Message, Customer_user, Chat_name
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()

class MyConsumer(AsyncWebsocketConsumer):
    async def authenticate_user(self):
        headers = dict(self.scope['headers'])
        token = None
        if b'authorization' in headers:
            auth_header = headers[b'authorization'].decode('utf-8')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        if token:
            try:
                UntypedToken(token)  
                user = await self.get_user(token) 
                return user
            except (AuthenticationFailed, InvalidToken, TokenError):
                return AnonymousUser()
        return AnonymousUser()




    async def connect(self):
        self.user = await self.authenticate_user()
        if self.user.is_anonymous:
            await self.close()
        else:
            await self.accept()
            self.chat_id = self.scope['url_route']['kwargs']['chat']
            self.user.status = True
            await self.update_message_status('connect')
            await database_sync_to_async(self.user.save)()

            chat_ids = await self.get_users_app()
            self.online_users = await self.get_online_user()

            for chat_id in chat_ids:
                num = int(self.user.id) + int(chat_id)
                chat_name = f'chat_{num}'
                await self.channel_layer.group_add(
                    chat_name,
                    self.channel_name
                )
                await self.channel_layer.group_send(
                    chat_name,
                    {
                        "type": "online",
                        "user_connectnow": self.user.id,
                        "users_online": self.online_users
                    }
                )

    async def online(self, event):
        await self.send(
            text_data=json.dumps({
                "status": "online",
                "user_connect_now": event['user_connectnow'],
                "users_online": event['users_online']
            })
        )


    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        
        chat_id = data['chat_name']
        
        id_recevier=chat_id.split('_')
        
        id_recevier=int(id_recevier[1])
        
        receiver_id = abs(int(self.user.id)-id_recevier)
        
        receiver_status = await self.get_user_status(int(receiver_id))
        
        message_type = 'connect' if receiver_status else 'disconnect'
        
        await self.save_message(chat_id=chat_id, sender=self.user.id, receiver=receiver_id, message=message, type_message=message_type)
        
        await self.channel_layer.group_send(
            chat_id,
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
        chat_name = Chat_name.objects.get(name=chat_id)
        sender_user = Customer_user.objects.get(id=sender)
        receiver_user = Customer_user.objects.get(id=receiver)
        
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
    def get_user(self, token):
        jwt_authenticator = JWTAuthentication()
        validated_token = jwt_authenticator.get_validated_token(token)
        return jwt_authenticator.get_user(validated_token)

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
