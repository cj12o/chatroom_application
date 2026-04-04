
from ..models.topic_model import Topic
from ..logger import logger
import math
import spacy

_nlp=None
def lazy_load_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_md")
    return _nlp


def get_embeddings(corpus: list):
    """Return list of vectors"""
    nlp=lazy_load_nlp()
    return [nlp(text).vector for text in corpus]
        

def cosine_sim(a, b):
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0

    return dot_product / (norm_a * norm_b)



def topic_assigner(topic_lst: list, user_topic: str):
    """Return most similar topic"""
    nlp=lazy_load_nlp()
    topic_embeddings = get_embeddings(topic_lst)
    user_embedding = nlp(user_topic).vector

    max_sim = -1
    best_topic = None

    for topic, topic_vec in zip(topic_lst, topic_embeddings):
        sim = cosine_sim(topic_vec, user_embedding)
        print(f"{topic} -> {sim:.4f}")

        if sim > max_sim:
            max_sim = sim
            best_topic = topic

    return best_topic


def topicsList(user_topic:str):
    """gets topic list from db and feeds to topic_assigner which gives parent_topic"""
    try:
        topics=Topic.objects.all()
        if len(topics)<1:raise Exception("No parent topics,Create ASAP ")

        topic_lst=[t.topic for t in topics]
        

    # user_topic="football"
        topic_similar=topic_assigner(topic_lst=topic_lst,user_topic=user_topic)
        return topic_similar
    except Exception as e:  
        logger.error(e)


