import os
import joblib
from django.conf import settings


MODEL_PATH = os.path.join(settings.BASE_DIR,r"base\moderator_model.pkl")

print("Loading moderation model from:", MODEL_PATH)
print("Exists?", os.path.exists(MODEL_PATH))

DATA = joblib.load(MODEL_PATH)
VECTORIZER = DATA["vectorizer"]
MODEL = DATA["model"]

# LABELS = [
#     "non_toxic","toxic", "severe_toxic", "obscene",
#     "threat", "insult", "identity_hate"
# ]
