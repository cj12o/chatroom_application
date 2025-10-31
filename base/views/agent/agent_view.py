from rest_framework.views import APIView

from concurrent.futures.thread import ThreadPoolExecutor
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async
import asyncio

from .room_agent import main

from multiprocessing import Pool

from ..admin_views import  LoginApiview

from .testSocket import connectTows


executor=ThreadPoolExecutor(max_workers=12)


class AgentApiviews(APIView):
    def get(self,request):
        try:
            "triggers agent testing"
            # executor.submit(main,)

            #todo :thread ->submit->pool
          
            login_obj=LoginApiview()
            dct_info={
                "email":"agent@email.com",
                "password":"agenticqwert4"
            }
            executor.submit(login_obj.post,dct_info)
            future=executor.submit(main,)
        
            future.add_done_callback(lambda f:asyncio.run(connectTows(future.result())))
            
            return Response({
                "agent_state":"triggered"
            },status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "agent_state":"not yet triggered",
                "error":str(e)
            },status=status.HTTP_400_BAD_REQUEST)
        finally:
            pass
            
    
