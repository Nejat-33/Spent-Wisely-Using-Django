from django import forms
from ..models import Expense, Category

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'descriprion', 'date']
        widgets = {
            'date' : forms.DateInput(attrs={'type': 'date'}),
        }

        def __init__(self, *args, **kargs):
            super().__init__(*args, **kargs)
            for field in self.fileds.values():
                field.widget.attrs.update({
                  'class': 'w-full bg-white/5 border border-white/10 rounded-xl p-3 focus:outline-none focus:border-blue-500 transition text-white'  
                })