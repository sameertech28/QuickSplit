from django.db import models
from django.contrib.auth.models import User
from groups.models import Group


class Settlement(models.Model):
    """A payment made to settle debts within a group."""

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('upi', 'UPI / Mobile Payment'),
        ('paypal', 'PayPal'),
        ('crypto', 'Cryptocurrency'),
        ('other', 'Other'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='settlements')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='settlements_paid')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='settlements_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NPR')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Settlement'
        verbose_name_plural = 'Settlements'

    def __str__(self):
        return f'{self.from_user.username} paid {self.to_user.username} {self.currency} {self.amount}'
