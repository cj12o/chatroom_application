from sentence_transformers import SentenceTransformer, util

from ..models.topic_model import Topic
from  ..serializers.topic_serializer import TopicSerializer

model=SentenceTransformer('all-MiniLM-L6-v2')

def topicsList(user_topic:str):
    topics=Topic.objects.all()
    serializer=TopicSerializer(topics,many=True)

    if serializer:
        topic_lst=[]
        # print(f"topic_lst:{topic_lst}")
        for dct in serializer.data:
            # print(f"Topics:{ele.topic}")
            for k,v in dct.items():
                if k=="topic":
                    topic_lst.append(str(dct[k].lower()))
                    # print(f"Topics:{dct[k]}")
        print(topic_lst)

    # user_topic="football"
    topic_similar=topicAssigner(topic_lst=topic_lst,user_topic=user_topic)
    return topic_similar


def topicAssigner(topic_lst:list,user_topic:str):
    topic_max_similar=""
    similarity=0
    v1=model.encode(user_topic)
    idx=0
    for topic in topic_lst:
        if idx==0:
            topic_max_similar=topic
            v2=model.encode(topic)
            similarity=util.cos_sim(v1, v2)
            
        else:
            v2=model.encode(topic)
            similarity_new= util.cos_sim(v1, v2)
            # print(f"{topic}:{similarity.item()}")
            if similarity< similarity_new:
                topic_max_similar=topic
                similarity=similarity_new
        idx+=1
    
    print(f"😀😀😀most similar:{topic_max_similar}")
    return topic_max_similar
    # return topic_max_similar

