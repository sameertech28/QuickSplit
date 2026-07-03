from django.db import models
from django.contrib.auth.models import User
from groups.models import Group


class Expense(models.Model):
    """An expense created by a group admin, visible to all members."""

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
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_expenses')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'

    def __str__(self):
        return f'{self.title} - {self.currency} {self.amount}'

    @property
    def total_contributed(self):
        """Sum of all member contributions for this expense."""
        return self.contributions.aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def remaining(self):
        """How much is still uncovered."""
        return self.amount - self.total_contributed


class Contribution(models.Model):
    """A self-reported payment by a member towards an expense.
    Each member can only add and delete their own contributions."""

    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='contributions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contribution'
        verbose_name_plural = 'Contributions'

    def __str__(self):
        return f'{self.user.username} paid {self.amount} for {self.expense.title}'
