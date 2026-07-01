from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


CURRENCY_CHOICES = [
    ('USD', 'US Dollar'), ('EUR', 'Euro'), ('GBP', 'British Pound'),
    ('INR', 'Indian Rupee'), ('NPR', 'Nepalese Rupee'), ('JPY', 'Japanese Yen'),
    ('AUD', 'Australian Dollar'), ('CAD', 'Canadian Dollar'), ('CHF', 'Swiss Franc'),
    ('CNY', 'Chinese Yuan'), ('SGD', 'Singapore Dollar'), ('AED', 'UAE Dirham'),
]


class UserProfile(models.Model):
    """Extended user profile with additional fields for QuickSplit."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(
        max_length=20, blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')]
    )
    default_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    bio = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username}'

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def initials(self):
        name = self.user.get_full_name()
        if name and len(name.split()) >= 2:
            parts = name.split()
            return f'{parts[0][0]}{parts[1][0]}'.upper()
        return (self.user.username[:2]).upper()
