
# import joblib

# label_names = [
#     "toxic", "severe_toxic", "obscene",
#     "threat", "insult", "identity_hate"
# ]


# def moderate(corpus:list[str]):
#     try:
#         model_path=r'C:\Users\BIT\Desktop\Chatroom\core\base\moderator_model.pkl'
#         data=joblib.load(model_path)
#         vectorizer=data['vectorizer']
#         model=data['model']

#         results=[]
#         for text in corpus:
#             chat_vec=vectorizer.transform([text])
#             result=model.predict(chat_vec)
#             results.append(result[0])
#         return results

#     except Exception as e:
#         print(f"Error:{str(e)}")


# if __name__=="__main__":
#     corpus=[
#         "Brown people are shit eaters",
#         "indians are dirt eaters"
#     ]
#     results=moderate(corpus=corpus)
#     for results 
#     print(results)


