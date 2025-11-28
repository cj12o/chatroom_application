
from ..models.topic_model import Topic
from ..logger import logger
from sentence_transformers import SentenceTransformer,util



def getEmbeddings(corpus:list):

    """return vector representation of topic"""
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        tensors=model.encode(corpus)
        return tensors
    
    except Exception as e: 
        logger.error(e)
        


def topicsList(user_topic:str):
    """gets topic list from db and feeds to topicAssigner which gives parent_topic"""
    try:
        topics=Topic.objects.all()
        if len(topics)<1:raise Exception("No parent topics,Create ASAP ")

        topic_lst=[t.topic for t in topics]
        

    # user_topic="football"
        topic_similar=topicAssigner(topic_lst=topic_lst,user_topic=user_topic)
        return topic_similar
    except Exception as e:  
        logger.error(e)


def topicAssigner(topic_lst:list,user_topic:str):
    """topic with max cosine similarity is returned"""
    try:
        topic_max_similar=None
        max_cosine_sim=0
        new_list=topic_lst.copy()
        new_list.append(user_topic)
        embeddings=getEmbeddings(new_list)

        user_topic_tensor=embeddings[len(topic_lst)]
    
        for idx,topic in enumerate(topic_lst):

            topic_tensor=embeddings[idx]
        

            cosine_similarity=util.cos_sim(topic_tensor,user_topic_tensor)[0][0]
            
            if max_cosine_sim<cosine_similarity:
                max_cosine_sim=cosine_similarity
                topic_max_similar=topic
            
        return topic_max_similar

    except Exception as e:
        logger.error(e)

