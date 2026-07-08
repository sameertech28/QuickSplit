from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    """A group of users who share expenses together."""

    CATEGORY_CHOICES = [
        ('trip', 'Trip'),
        ('home', 'Home'),
        ('couple', 'Couple'),
        ('dinner', 'Dinner'),
        ('office', 'Office'),
        ('other', 'Other'),
    ]

    CURRENCY_CHOICES = [
        ('NPR', 'Nepalese Rupee (NPR)'),
        ('USD', 'US Dollar (USD)'),
        ('EUR', 'Euro (EUR)'),
        ('INR', 'Indian Rupee (INR)'),
        ('GBP', 'British Pound (GBP)'),
        ('AUD', 'Australian Dollar (AUD)'),
        ('CAD', 'Canadian Dollar (CAD)'),
        ('SGD', 'Singapore Dollar (SGD)'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, through='GroupMember', related_name='expense_groups')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='NPR')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.group_members.count()

    @property
    def total_expenses(self):
        return self.expenses.aggregate(total=models.Sum('amount'))['total'] or 0


class GroupMember(models.Model):
    """Through model for User-Group relationship with role metadata."""

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_members')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    nickname = models.CharField(max_length=100, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')
        verbose_name = 'Group Member'
        verbose_name_plural = 'Group Members'

    def __str__(self):
        return f'{self.user.username} in {self.group.name}'

    @property
    def display_name(self):
        return self.nickname or self.user.get_full_name() or self.user.username


class Invitation(models.Model):
    """An invitation for a user (by email) to join a group."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'email')
        verbose_name = 'Invitation'
        verbose_name_plural = 'Invitations'

    def __str__(self):
        return f"{self.email} to {self.group.name} ({self.status})"

