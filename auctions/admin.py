# auctions/admin.py
from django.contrib import admin
from .models import LuxuryShoe, Bid

@admin.register(LuxuryShoe)
class LuxuryShoeAdmin(admin.ModelAdmin):
    list_display = ('get_product_name', 'starting_bid', 'auction_start', 'auction_end', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('product__product_name',)
    fields = ('product', 'starting_bid', 'auction_start', 'auction_end')  # Removed is_active from editable fields
    readonly_fields = ('is_active',)  # Make is_active read-only

    def get_product_name(self, obj):
        return obj.product.product_name
    get_product_name.short_description = 'Product Name'

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('luxury_shoe', 'user', 'amount', 'timestamp')
    list_filter = ('luxury_shoe',)
    search_fields = ('user__username',)