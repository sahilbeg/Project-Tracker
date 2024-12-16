# filters.py

from django.contrib.admin import SimpleListFilter
from .models import Account

class AccountOwnerFilter(SimpleListFilter):
    title = 'Account'  # Label to display in the filter sidebar
    parameter_name = 'account'

    def lookups(self, request, model_admin):
        # Only return the accounts that the logged-in user owns
        accounts = Account.objects.filter(owner=request.user)
        return [(account.id, account.name) for account in accounts]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(account_id=self.value())
        return queryset
