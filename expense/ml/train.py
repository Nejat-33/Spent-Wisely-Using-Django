
import joblib
import os
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd



df = pd.read_csv('personal_expense_classification.csv')

df["unified_text"] = df["merchant"].astype('str') + " " + df["description"].astype('str')

df["unified_text"] = df["unified_text"].str.lower().str.strip()

descriptions = df["unified_text"]
labels = df["category"]

X_train, X_test, y_train, y_test = train_test_split(
    descriptions, labels, test_size=0.2, random_state=42
)


pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),  
        min_df=1,
        lowercase=True,
        stop_words="english",
    )),
    ("clf", LogisticRegression(
        max_iter=1000,
        C=1.0,
        solver="lbfgs",
    )),
])

pipeline.fit(X_train, y_train)

print(classification_report(y_test, pipeline.predict(X_test)))


MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)
joblib.dump(pipeline, os.path.join(MODEL_DIR, "category_classifier.pkl"))
print("Model saved to expenses/ml/models/category_classifier.pkl")