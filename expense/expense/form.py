from django import forms
from ..models import Expense, Category
from django.db.models import Q

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'description', 'date']
        widgets = {
            'date' : forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
            user = kwargs.pop('user', None)
            super().__init__(*args, **kwargs)
            if user:
              self.fields['category'].queryset = Category.objects.filter(
                Q(user__isnull=True) | Q(user=user)
            )
            else:
               self.fields['category'].queryset = Category.objects.filter(user__isnull=True)  
            for field in self.fields.values():
                field.widget.attrs.update({
                  'class': 'w-full bg-white/5 border border-white/10 rounded-xl p-3 focus:outline-none focus:border-blue-500 transition text-white'  
                })