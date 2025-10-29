from rest_framework.views import APIView

from concurrent.futures.thread import ThreadPoolExecutor
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async

from .room_agent import main

from multiprocessing import Pool

from ..admin_views import  LoginApiview



executor=ThreadPoolExecutor(max_workers=12)

class AgentApiviews(APIView):
    def get(self,request):
        try:
            "triggers agent testing"
            # executor.submit(main,)

            #todo :thread ->submit->pool
            # executor.submit(trigger)
            login_obj=LoginApiview()
            dct_info={
                "email":"agent@email.com",
                "password":"agenticqwert4"
            }
            executor.submit(login_obj.post,dct_info)
            executor.submit(main,)

            return Response({
                "agent_state":"triggered"
            },status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "agent_state":"not yet triggered",
                "error":str(e)
            },status=status.HTTP_400_BAD_REQUEST)
    

def trigger():
    try:
        """
        simultaneously  login Llm & start agent
        """
        print(f"TRIGGER func called")

        login_obj=LoginApiview()
        dct_info={
            "email":"agent@email.com",
            "password":"agenticqwert4"
        }
        executor.submit(login_obj.post,dct_info)
        executor.submit(main,)
    
        # with Pool(4) as p:
        #     p.apply(main,[])

        executor.shutdown()
        print(f"Trigger complete ")
    except Exception as e:
        print(f"❌❌Error in agent run :{str(e)}")