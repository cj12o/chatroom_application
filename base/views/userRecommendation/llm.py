# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate


# llm=ChatOpenAI(
#     base_url="http://127.0.0.1:1239/v1/",
#     model="hermes-3-llama-3.2-3b",
#     api_key="lm_studio"
# )



# template = ChatPromptTemplate.from_messages(
#     [
#         ("system", """

#         Role:You are a chatroom recommender .
         
#         list_of_rooms:{room_lst}

         
#         Follow these rules :
#         1)only choose rooms from list_of_rooms
#         2)user history :{user_history_lst}

#         Based on user history give a list sorted in decreasing order of recommendation
#         and provide short reason for selecting it
#         """),
#     ]
# )




# def Recommend(room_list:list,user_history:list): 
#     prompt = template.format_messages(
#         room_lst=room_list,
#         user_history_lst=user_history
#     )

#     response=llm.invoke(prompt)
#     print(f"LLm response:{response.content}")

