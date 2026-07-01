from django.db import models
from django.contrib.auth.models import User
from groups.models import Group


class Expense(models.Model):
    """An expense paid by one user, split among group members."""

    SPLIT_METHOD_CHOICES = [
        ('equal', 'Equal Split'),
        ('percentage', 'Percentage Based'),
        ('custom', 'Custom Amounts'),
        ('item', 'Item Based'),
    ]

    CATEGORY_CHOICES = [
        ('food', 'Food & Dining'),
        ('transport', 'Transportation'),
        ('accommodation', 'Accommodation'),
        ('entertainment', 'Entertainment'),
        ('shopping', 'Shopping'),
        ('utilities', 'Utilities'),
        ('groceries', 'Groceries'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paid_expenses')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    split_method = models.CharField(max_length=20, choices=SPLIT_METHOD_CHOICES, default='equal')
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)
    is_settled = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'

    def __str__(self):
        return f'{self.title} - {self.currency} {self.amount}'


class ExpenseSplit(models.Model):
    """How an expense is split among individual users."""

    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_splits')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_settled = models.BooleanField(default=False)
    settled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('expense', 'user')
        verbose_name = 'Expense Split'
        verbose_name_plural = 'Expense Splits'

    def __str__(self):
        return f'{self.user.username} owes {self.amount} for {self.expense.title}'
