from django import forms
from .models import Expense, Contribution


class ExpenseForm(forms.ModelForm):
    """Form for admins to create/edit an expense."""

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'currency', 'category', 'description', 'receipt_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name == 'receipt_image':
                field.widget.attrs.update({'class': 'form-control bg-dark text-light border-secondary'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select bg-dark text-light border-secondary'})
            else:
                field.widget.attrs.update({'class': 'form-control bg-dark text-light border-secondary'})


class ContributionForm(forms.ModelForm):
    """Form for any group member to record their own payment."""

    class Meta:
        model = Contribution
        fields = ['amount', 'note']
        widgets = {
            'note': forms.TextInput(attrs={'placeholder': 'e.g. Paid via UPI'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control bg-dark text-light border-secondary'})
        self.fields['amount'].widget.attrs['placeholder'] = 'Amount you paid'
        self.fields['amount'].widget.attrs['min'] = '0.01'
        self.fields['amount'].widget.attrs['step'] = '0.01'
        self.fields['note'].required = False
