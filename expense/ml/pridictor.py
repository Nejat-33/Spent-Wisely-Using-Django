# expenses/ml/predictor.py

import joblib
import os
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "category_classifier.pkl")

class CategoryPredictor:
    _instance = None
    _pipeline = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Model not found. Run: python expenses/ml/train.py"
            )
        self._pipeline = joblib.load(MODEL_PATH)

    def predict(self, description: str) -> dict:
        if not description or not description.strip():
            return {"category": None, "confidence": 0.0, "all_scores": {}}

        desc = description.strip().lower()
        category = self._pipeline.predict([desc])[0]
        probabilities = self._pipeline.predict_proba([desc])[0]
        classes = self._pipeline.classes_

        all_scores = {
            cls: round(float(prob), 3)
            for cls, prob in zip(classes, probabilities)
        }

        confidence = round(float(np.max(probabilities)), 3)

        return {
            "category": category,
            "confidence": confidence,  
            "all_scores": all_scores,      
        }