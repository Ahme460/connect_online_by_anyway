from channels.generic.websocket import AsyncWebsocketConsumer
import json
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from .models import Message, Customer_user
import django
from django.utils import timezone
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

# استرجاع موديل المستخدم
User = get_user_model()

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # استخراج الهيدر الذي يحتوي على التوكن
        headers = dict(self.scope['headers'])
        token = None
        
        # البحث عن التوكن في الهيدر
        if b'authorization' in headers:
            auth_header = headers[b'authorization'].decode('utf-8')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        if token:
            try:
                UntypedToken(token)  # التحقق من التوكن
                self.user = await self.get_user(token)  # استرجاع المستخدم من التوكن
            except (AuthenticationFailed, InvalidToken, TokenError):
                self.user = AnonymousUser()
        else:
            self.user = AnonymousUser()

        if self.user.is_anonymous:
            await self.close()
        else:
            
            await self.accept()
            self.chat_id = self.scope['url_route']['kwargs']['chat']
            self.user.status=True
            await self.get_message()
            await database_sync_to_async(self.user.save)()
        
        chat_ids= await self.get_users_app()
        
        self.online_= await self.get_online_user()
        
        for chat_id in chat_ids:
            print(chat_id)
            print("eroor fuckkkkkkkkkkkkkkkkkkkkkk")
            print(self.user.id)
            num=int(self.user.id)+int(chat_id)
            
            chat_name = f'chat_{num}'
            
            await self.channel_layer.group_add(
                chat_name,
                self.channel_name
            )
        #
       #$ print(user)
      #  print("//////////////////////////////////////////")
        
            
            await self.channel_layer.group_send(
                chat_name,
                {
                    "type":"online",
                    "user_connectnow":self.user.id,
                    "users_online": self.online_
                     
                   
                }
            )
        
            
       
    async def online(self,event):
        print("slef online ____________________________________________________")
        print(self.online_)
        await self.send(
           text_data= json.dumps(
               {
                   "status":"online",
                   "user_connect_now":event['user_connectnow'],
                   "users_online":event['users_online']
                   
               }
           )
        )
        
        
    
    @database_sync_to_async
    def get_online_user(self):    
        user=Customer_user.objects.filter(status=True).exclude(id=self.user.id).values_list('id', flat=True)
        return list(user)
    
    

    @database_sync_to_async
    def get_user(self, token):
        """
        هذه الدالة تقوم بفك التوكن JWT واسترجاع المستخدم المرتبط به.
        """
        jwt_authenticator = JWTAuthentication()
        validated_token = jwt_authenticator.get_validated_token(token)
        return jwt_authenticator.get_user(validated_token)
    
    
    
    
    @database_sync_to_async
    def get_message(self):
        message=Message.objects.filter(receiver=self.user).update(type_message='connect')
         #.values_list('type_message',flat=True)
        
        
    
    
    @database_sync_to_async
    def get_users_app(self):
        print(list(Customer_user.objects.all().exclude(id=self.user.id).values_list('id', flat=True)))
        return list(Customer_user.objects.all().exclude(id=self.user.id).values_list('id', flat=True))


    
    

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        chat=data['chat_name']
        receiver = data['receiver']
        user_status=await self.about_user(int(receiver))
        if user_status:
            await self.save_message(sender=self.user.id, receiver=receiver, message=message,type_message='connect')
        else:
            await self.save_message(sender=self.user.id, receiver=receiver, message=message,type_message='disconnect')
        await self.channel_layer.group_send(
            chat,
            {
                "type": "chat_message",
                "message": message,
                "sender":self.user.id,
                "receiver": receiver
            }
        )
    async def disconnect(self, close_code):
        # التحقق إذا كانت الخاصية chat_name موجودة قبل استخدامها
        chat_ids= await self.get_users_app()
        self.user.status = False
        self.user.last_seen = timezone.now()  # تعيين الوقت الحالي
            # يمكن تحديث الحالة أيضًا إذا كان ذلك مطلوبًا
        await database_sync_to_async(self.user.save)() 
        print(self.user.id)
        print(self.online_)
        print(":::::::::::::::::::::::::::::::")
        #list(self.online_).remove(self.user.id)
        for chat_id in chat_ids:
            num=int(self.user.id)+int(chat_id)
            chat_name = f'chat_{num}'
            await self.channel_layer.group_discard(
                chat_name,
                self.channel_name
            )
            await self.channel_layer.group_send(
                chat_name,
                {
                    'type':'send_dis',
                    'user_id':self.user.email           
                }
            )
            
            
            
    async def send_dis(self,event):
        user=event['user_id']
        
        await self.send(
            text_data=json.dumps({
             'status': 'offline',
             'last_seen':str(timezone.now()),
            'user_id': user,
            
            "users_online":list(self.online_)
            
            
            
            }
                                 
            )
        )
    
    
    @database_sync_to_async
    
    def about_user(self,id_user:int):    
        user=Customer_user.objects.get(id=id_user)
        return user.status
    
    async def chat_message(self, event):
        message = event['message']
        sender=event['sender']
        receiver = event['receiver']
        await self.send(
            text_data=json.dumps(
                {
                    'message': message,
                    'sender':sender,
                    'receiver': receiver
                }
            )
        )

    @database_sync_to_async
    def save_message(self, sender, receiver, message,type_message):
        print("____________________________________________________________________")
        print(sender)
        print(receiver)
        print(message)
        print("____________________________________________________________________")
        # الحصول على كائنات المستخدمين المرسل والمستقبل
        sender_user = Customer_user.objects.get(id=int(sender))
        receiver_user = Customer_user.objects.get(id=int(receiver))
        
        # إنشاء مثيل الرسالة باستخدام كائنات المستخدم
        return Message.objects.create(
            message=str(message),
            sender=sender_user,  # استخدم كائن المستخدم بدلاً من ID
            receiver=receiver_user ,
            type_message=type_message
            
            # استخدم كائن المستخدم بدلاً من ID
        )