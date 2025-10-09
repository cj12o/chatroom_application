from langchain_openai import ChatOpenAI


llm=ChatOpenAI(
    base_url="http://127.0.0.1:1239/v1/",
    model="mistralai/mistral-nemo-instruct-2407",
    api_key="lm_studio"
)






