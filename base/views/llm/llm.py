from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

llm=ChatOpenAI(
    base_url="http://127.0.0.1:1239/v1/",
    model="mistralai/mistral-nemo-instruct-2407",
    api_key="lm_studio"
)

# "choices": [
#     {
#       "index": 0,
#       "logprobs": null,
#       "finish_reason": "stop",
#       "message": {
#         "role": "assistant",
#         "content": "It's always sunny in San Francisco!"
#       }
#     }
#   ],
class Response(BaseModel):
    reply:str

def get_weather(city: str) -> str:  
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

def calculate(n1:int,n2:int)->int:
    """return sum of numbers"""
    return f"sum of {n1}+{n2}={n1+n2}"


agent = create_react_agent(
    model=llm,
    tools=[get_weather,calculate],  
    prompt="You are a helpful assistant",
    response_format=Response 
)

while True:
    user=input("user:")
    if user in ["quit" ,"exit"]:
        break
    response=agent.invoke(
        {"messages": [{"role": "user", "content":user}]}
        )
    print(response["structured_response"])





