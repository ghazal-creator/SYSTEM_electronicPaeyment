from django.contrib import admin

from .models import *


admin.site.register(User)
admin.site.register(Currency)
admin.site.register(WalletType)
admin.site.register(Wallet)
admin.site.register(ServiceCategory)
admin.site.register(ServiceType)
admin.site.register(Transaction)
admin.site.register(Receipt)
admin.site.register(Branch)
admin.site.register(Institution)
admin.site.register(Notification_Transactions)
admin.site.register(FrequentContact)
admin.site.register(TransactionCategory)
admin.site.register(AuditLog)
admin.site.register(Payment)
admin.site.register(Admin)
admin.site.register(UserPreference)
admin.site.register(Notification)
