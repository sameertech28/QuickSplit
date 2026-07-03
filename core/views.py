from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count
from .forms import SignUpForm, LoginForm, UserProfileForm
from groups.models import Group, GroupMember, Invitation
from expenses.models import Expense, Contribution


def landing_page(request):
    """Public landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


def signup_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Welcome to QuickSplit. Your account has been created.')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid credentials. Please try again.')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """User logout."""
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('landing')


@login_required
def dashboard_view(request):
    """Main dashboard showing groups, balances, and activity."""
    user = request.user
    memberships = GroupMember.objects.filter(user=user).select_related('group')
    groups = [m.group for m in memberships]

    # Calculate summary stats
    total_contributed = Contribution.objects.filter(
        user=user
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_created_expenses = Expense.objects.filter(
        created_by=user
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    recent_expenses = Expense.objects.filter(
        group__in=groups
    ).select_related('created_by', 'group').order_by('-date')[:10]

    # Fetch pending invitations for this user (case-insensitive)
    pending_invitations = Invitation.objects.filter(email__iexact=user.email, status='pending').select_related('group', 'invited_by')

    context = {
        'groups': groups,
        'total_contributed': total_contributed,
        'total_created_expenses': total_created_expenses,
        'recent_expenses': recent_expenses,
        'group_count': len(groups),
        'pending_invitations': pending_invitations,
    }
    return render(request, 'dashboard.html', context)


@login_required
def profile_view(request):
    """User profile view and edit."""
    profile = request.user.profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update User model fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })

    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'auth/profile.html', context)
