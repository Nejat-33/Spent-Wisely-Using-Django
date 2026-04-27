from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    descriprion = models.TextField()
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=8)
    month = models.IntegerField()
    year = models.IntegerField()

    def __cl__(self):
        return f"{self.user.username} - {self.month}/{self.year}"

