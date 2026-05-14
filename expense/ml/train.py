# expenses/ml/train.py

import joblib
import os
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd

# TRAINING_DATA = [
#     # Food & Dining
#     ("lunch at kfc", "Food & Dining"),
#     ("dinner with friends", "Food & Dining"),
#     ("coffee at starbucks", "Food & Dining"),
#     ("grocery shopping at shoa", "Food & Dining"),
#     ("pizza delivery", "Food & Dining"),
#     ("breakfast sandwich", "Food & Dining"),
#     ("supermarket weekly shop", "Food & Dining"),
#     ("restaurant bill", "Food & Dining"),

#     # Transport
#     ("uber ride to airport", "Transport"),
#     ("taxi fare", "Transport"),
#     ("bus ticket", "Transport"),
#     ("fuel for car", "Transport"),
#     ("parking fee downtown", "Transport"),
#     ("minibus ride", "Transport"),
#     ("ride share to office", "Transport"),

#     # Utilities
#     ("electricity bill", "Utilities"),
#     ("water bill payment", "Utilities"),
#     ("internet subscription ethiotel", "Utilities"),
#     ("phone top up", "Utilities"),
#     ("gas bill", "Utilities"),
#     ("wifi monthly charge", "Utilities"),

#     # Shopping
#     ("bought new shoes", "Shopping"),
#     ("amazon order", "Shopping"),
#     ("clothing store", "Shopping"),
#     ("electronics purchase", "Shopping"),
#     ("bookstore", "Shopping"),
#     ("online order delivery", "Shopping"),

#     # Health
#     ("pharmacy prescription", "Health"),
#     ("doctor consultation", "Health"),
#     ("gym membership", "Health"),
#     ("hospital visit", "Health"),
#     ("dental checkup", "Health"),
#     ("vitamins and supplements", "Health"),

#     # Entertainment
#     ("netflix subscription", "Entertainment"),
#     ("movie tickets", "Entertainment"),
#     ("spotify monthly", "Entertainment"),
#     ("concert tickets", "Entertainment"),
#     ("video game purchase", "Entertainment"),
#     ("youtube premium", "Entertainment"),

#     # Education
#     ("online course fee", "Education"),
#     ("university tuition", "Education"),
#     ("textbooks purchase", "Education"),
#     ("udemy course", "Education"),
#     ("exam registration", "Education"),

#     # Rent & Housing
#     ("monthly rent payment", "Rent & Housing"),
#     ("house rent", "Rent & Housing"),
#     ("apartment deposit", "Rent & Housing"),
#     ("maintenance fee", "Rent & Housing"),
# ]

df = pd.read_csv('personal_expense_classification.csv')

df["unified_text"] = df["merchant"].astype('str') + " " + df["description"].astype('str')

df["unified_text"] = df["unified_text"].str.lower().str.strip()

print(df["unified_text"])


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