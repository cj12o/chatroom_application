from ...models import History,Room

from django.db.models import Q
K=5






def getRoomDet(topK:int,session_lst:list)->list:
    room_lst=[]
    for session in session_lst:
        history=History.objects.filter(Q(session=session)).order_by('-created_at')[0:topK]
        for obj in history:
            dct={"name":obj.rooms_visited.name,"id":obj.rooms_visited.id,"description":obj.rooms_visited.description}
            room_lst.append(dct)
    
    # print(f"✅✅Room list :{room_lst}")
    return room_lst


#Method that return top k or less session
def gettopksesh(username:str)->list:
    getTopsesh=History.objects.filter(Q(user__username=username)).order_by('-created_at')

    sesh_lst=[]
    for obj in getTopsesh:
        if len(sesh_lst)>K:
            break
        if obj.session not in sesh_lst:
            sesh_lst.append(obj.session) 
    # print(f"✅✅Top k sesh:{sesh_lst}")
    return getRoomDet(topK=3,session_lst=sesh_lst)

