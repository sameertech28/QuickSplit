from django import forms
from .models import Settlement
from groups.models import GroupMember

class SettlementForm(forms.ModelForm):
    class Meta:
        model = Settlement
        fields = ['to_user', 'amount', 'currency', 'payment_method', 'notes']
        widgets = {
            'to_user': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes about this payment...'}),
        }

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.group and self.user:
            # Only allow selecting users in the same group, excluding the current user
            group_members = GroupMember.objects.filter(group=self.group).select_related('user')
            users_in_group = [member.user.id for member in group_members if member.user != self.user]
            self.fields['to_user'].queryset = self.fields['to_user'].queryset.filter(id__in=users_in_group)
            
            # Simple list of currencies for the dropdown
            self.fields['currency'].widget = forms.Select(choices=[
                ('USD', 'USD ($)'),
                ('EUR', 'EUR (€)'),
                ('GBP', 'GBP (£)'),
                ('INR', 'INR (₹)'),
            ], attrs={'class': 'form-select'})
