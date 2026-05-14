# expenses/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Expense
import csv, os

FEEDBACK_CSV = "expenses/ml/data/user_feedback.csv"

@receiver(post_save, sender=Expense)
def collect_training_feedback(sender, instance, created, **kwargs):
    if created and instance.description and instance.category:
        os.makedirs(os.path.dirname(FEEDBACK_CSV), exist_ok=True)
        with open(FEEDBACK_CSV, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([instance.description, instance.category])