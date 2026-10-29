import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Demo training data
data = {
    "text": [
        "Pay registration fee to get internship",
        "Guaranteed job with no interview pay now",
        "Send money to confirm your internship seat",
        "Earn huge salary without any skills",
        "Pay security deposit before joining",
        "Official internship with technical interview",
        "Software developer internship with mentorship",
        "Apply through company careers website",
        "Python internship with project experience",
        "Internship selection based on skills and interview"
    ],
    "label": [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
}

df = pd.DataFrame(data)

model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", LogisticRegression(max_iter=1000))
])

model.fit(df["text"], df["label"])

joblib.dump(model, "internship_model.pkl")

print("Model trained and saved successfully!")