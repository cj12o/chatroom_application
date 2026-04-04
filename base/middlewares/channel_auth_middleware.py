# from channels.middleware import BaseMiddleware
# from channels.db import database_sync_to_async
# from rest_framework.authtoken.models import Token
# from base.models.userprofile_model import UserProfile
# from django.contrib.auth.models import AnonymousUser

#Note:basemiddleware ensures that when ever connection is established it runs

# def get_token_user(token_given:str):
#     try:
#         token=Token.objects.get(key=token_given)
#         return token.user
#     except Exception as e:
#         print(f"...Error in get_token_user_middleware_func:{e}")
#         return AnonymousUser()

# #wrapping so it can be called in  async fun
# get_token_user=database_sync_to_async(get_token_user)


# class TokenAuthChannelMiddleware(BaseMiddleware):
#     """ 
#     it gets the user and flags it online in db
#     """
    
#     async def __call__(self,scope,receive,send):
        
#         # print(f"scope middleware :{scope}")
#         token=scope["query_string"].decode()
#         token=token[6:len(token)]
        
#         if token:
#             scope["user"]=await get_token_user(token)
#             scope["username"]=user.username
#             scope["user_id"]=user.id
#         else:
#             scope["user"]=AnonymousUser()                
        
#         return await super().__call__(scope,receive,send)


from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def get_token_user(token_given: str):
    try:
        token = Token.objects.get(key=token_given)
        return token.user
    except Exception:
        return AnonymousUser()


class TokenAuthChannelMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):

        query_string = scope.get("query_string", b"").decode()

        # safer parsing
        token = None
        if "token=" in query_string:
            token = query_string.split("token=")[-1]

        if token:
            user = await get_token_user(token)   # ✅ FIXED
        else:
            user = AnonymousUser()

        # ✅ Assign AFTER resolving
        scope["user"] = user

        # Optional extras
        scope["username"] = getattr(user, "username", None)
        scope["user_id"] = getattr(user, "id", None)

        return await super().__call__(scope, receive, send)