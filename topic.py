import spacy
import math

nlp = spacy.load("en_core_web_md")

PARENT_TOPIC = ["sport", "entertainment", "politics", "business"]


def get_embeddings(corpus: list):
    """Return list of vectors"""
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


if __name__ == "__main__":
    result = topic_assigner(PARENT_TOPIC, "leo messi ")
    print("Best match:", result)