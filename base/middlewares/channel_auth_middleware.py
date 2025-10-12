from channels.middleware import BaseMiddleware
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token
from base.models.userprofile_model import UserProfile

#Note:basemiddleware ensures that when ever connection is established it runs

def get_token_user(token_given:str):
    
        token=Token.objects.get(key=token_given)
        userProf=UserProfile.objects.get(user__username=token.user.username)
        userProf.is_online=True
        userProf.save()
        return token.user.username


#wrapping so it can be called in  async fun
get_token_user=database_sync_to_async(get_token_user)


class TokenAuthChannelMiddleware(BaseMiddleware):
    """ 
    it gets the user and flags it online in db
    """
    async def __call__(self,scope,receive,send):
        token=scope["query_string"].decode()
        token=token[6:len(token)]

        # print(f"👤👤Token:{token}")
        username=await get_token_user(token)
        scope["username"]=username
        print(f"User:{scope["username"]}")
        return await super().__call__(scope,receive,send)
        
    
