
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

def get_model(model_name):
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")
    if not api_key:
        print("❌❌ API key is not set (checked OPENAI_API_KEY and LLM_API_KEY)")
        return None
    os.environ["OPENAI_API_KEY"] = api_key
    model = init_chat_model(model_name)
    return model

def get_model_with_structed_output(model_name:str,schema):
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")
    if not api_key:
        print("❌❌ API key is not set (checked OPENAI_API_KEY and LLM_API_KEY)")
        return None
    os.environ["OPENAI_API_KEY"] = api_key
    model = init_chat_model(model_name)
    return model.with_structured_output(schema)



def get_model_for_stream(model_name):
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")
    if not api_key:
        print("❌❌ API key is not set (checked OPENAI_API_KEY and LLM_API_KEY)")
        return None
    os.environ["OPENAI_API_KEY"] = api_key
    model = init_chat_model(model_name, streaming=True)
    return model

