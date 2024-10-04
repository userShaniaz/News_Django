from django.contrib import admin
from .models import *

# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'wallet')
#     list_display_links = ('id', 'name', 'wallet')
#     search_fields = ('name',)
#     list_filter = ('name', 'wallet')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', )

class KuponAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'active')

class CreditAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')

class BankCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'card_type', 'expiry_date', 'card_number')
    search_fields = ('user__username', 'card_number', 'card_type')
    readonly_fields = ('card_number',)

admin.site.register(CustomUser)
admin.site.register(Transaction)
admin.site.register(Kupon, KuponAdmin)
admin.site.register(Credit, CreditAdmin)
admin.site.register(BankCard, BankCardAdmin)