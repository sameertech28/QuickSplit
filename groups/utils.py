from decimal import Decimal
from django.db.models import Sum

def calculate_group_balances(group):
    """
    Calculates the net balance for every user in the group.
    Positive balance means they are owed money.
    Negative balance means they owe money.
    """
    members = list(group.group_members.select_related('user').all())
    member_count = len(members)
    
    if member_count == 0:
        return {}
        
    # Total expenses in the group
    total_expenses = group.expenses.aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
    share_per_person = total_expenses / Decimal(member_count)
    
    balances = {}
    for member in members:
        user = member.user
        
        # 1. How much did they contribute directly to expenses?
        contributions = user.contributions.filter(expense__group=group).aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
        
        # 2. How much have they paid to others via settlements?
        settlements_paid = user.settlements_paid.filter(group=group, is_completed=True).aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
        
        # 3. How much have they received from others via settlements?
        settlements_received = user.settlements_received.filter(group=group, is_completed=True).aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
        
        # Net amount they have effectively paid out of pocket
        total_paid_out = contributions + settlements_paid - settlements_received
        
        # Balance = What they paid - What they should have paid
        net_balance = total_paid_out - share_per_person
        
        balances[user.id] = {
            'user': user,
            'balance': round(net_balance, 2),
            'abs_balance': round(abs(net_balance), 2),
            'display_name': member.display_name,
            'total_paid': round(total_paid_out, 2),
            'share': round(share_per_person, 2)
        }
        
    return {
        'balances': balances,
        'total_expenses': round(total_expenses, 2),
        'share_per_person': round(share_per_person, 2)
    }


def get_suggested_settlements(balances_dict):
    """
    Takes a dictionary of user balances and generates an optimized list 
    of suggested payments (who owes whom and how much).
    """
    # Separate into debtors and creditors
    debtors = []
    creditors = []
    
    for user_id, data in balances_dict.items():
        if data['balance'] < -0.01:
            debtors.append({'user': data['user'], 'display_name': data['display_name'], 'amount': abs(data['balance'])})
        elif data['balance'] > 0.01:
            creditors.append({'user': data['user'], 'display_name': data['display_name'], 'amount': data['balance']})
            
    # Sort by amount descending to minimize transactions
    debtors.sort(key=lambda x: x['amount'], reverse=True)
    creditors.sort(key=lambda x: x['amount'], reverse=True)
    
    suggestions = []
    
    i = 0  # debtor index
    j = 0  # creditor index
    
    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]
        
        # Determine the settlement amount (the minimum of what the debtor owes and what the creditor is owed)
        settle_amount = min(debtor['amount'], creditor['amount'])
        
        if settle_amount > 0:
            suggestions.append({
                'from_user': debtor['user'],
                'from_name': debtor['display_name'],
                'to_user': creditor['user'],
                'to_name': creditor['display_name'],
                'amount': round(settle_amount, 2)
            })
            
        # Update remaining amounts
        debtors[i]['amount'] -= settle_amount
        creditors[j]['amount'] -= settle_amount
        
        # Move to next person if fully settled
        if debtors[i]['amount'] < Decimal('0.01'):
            i += 1
        if creditors[j]['amount'] < Decimal('0.01'):
            j += 1
            
    return suggestions
