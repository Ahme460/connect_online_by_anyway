import json
from channels.db import database_sync_to_async
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed



class CustomAuthMiddleware:
    """
    Custom authentication middleware for Django Channels that authenticates
    WebSocket connections based on a token or session information.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        token = None
        headers = {key.decode():value.decode() for key,value in scope.get('headers', {})}
        if 'authorization' in headers:
            token = headers['authorization']

        user = await self.authenticate_user(token)
        query_string = parse_qs(scope.get('query_string', b'').decode())

        if user is None:
            await send({
                "type": "websocket.close",
                "code": 4000,  # 4000 is a custom close code for unauthorized
            })
            return
        scope['user'] = user
        scope['headers'] = headers
        scope['query_string'] = query_string
        await self.inner(scope, receive, send)

    
    async def authenticate_user(self, token):
        """
        Authenticate the user by token.
        You can replace this with your custom authentication logic.
        """
        if token:
            try:
                UntypedToken(token)  
                user = await self.get_user(token) 
                return user
            except (AuthenticationFailed, InvalidToken, TokenError):
                return None
        return None

    @database_sync_to_async
    def get_user(self, token):
        jwt_authenticator = JWTAuthentication()
        validated_token = jwt_authenticator.get_validated_token(token)
        return jwt_authenticator.get_user(validated_token)