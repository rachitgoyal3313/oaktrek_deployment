# auctions/models.py
from django.db import models
from Store.models import Product
from Profile.models import User
from django.utils import timezone

class LuxuryShoe(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='luxury_auctions')
    starting_bid = models.FloatField()
    auction_start = models.DateTimeField()
    auction_end = models.DateTimeField(null=True, blank=True)  # Keep nullable to avoid migration error
    is_active = models.BooleanField(default=True, editable=False)  # Non-editable field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Auction for {self.product.product_name}"
    
    def save(self, *args, **kwargs):
        # Automatically determine is_active based on current time
        now = timezone.now()
        if self.auction_start and self.auction_end:
            self.is_active = self.auction_start <= now < self.auction_end
        else:
            self.is_active = False  # Inactive if auction_start or auction_end is not set
        super().save(*args, **kwargs)

    @property
    def status(self):
        """Helper property to display auction status."""
        now = timezone.now()
        if not self.auction_start or not self.auction_end:
            return "Incomplete"
        if now < self.auction_start:
            return "Upcoming"
        elif self.auction_start <= now < self.auction_end:
            return "Active"
        else:
            return "Ended"

class Bid(models.Model):
    luxury_shoe = models.ForeignKey(LuxuryShoe, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bid {self.amount} on {self.luxury_shoe.product.product_name}"
        
    class Meta:
        ordering = ['-timestamp']  # Default ordering by latest bids first