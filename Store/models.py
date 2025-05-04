from django.db import models
from django.conf import settings
from Profile.models import User
from django.utils.text import slugify
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(max_length=200, required=False)
    message = forms.CharField(widget=forms.Textarea, required=True)

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Skincare', 'Skincare'),
        ('Haircare', 'Haircare'),
        ('Bodycare', 'Bodycare'),
    ]

    GENDER_CHOICES = [
        ('Unisex', 'Unisex'),
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    product_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    category_slug = models.SlugField(blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    price = models.FloatField()
    rating = models.FloatField(default=0.0)
    image_1 = models.ImageField(upload_to='assets/products', blank=True, null=True)
    image_2 = models.ImageField(upload_to='assets/products', blank=True, null=True)
    image_3 = models.ImageField(upload_to='assets/products', blank=True, null=True)
    image_4 = models.ImageField(upload_to='assets/products', blank=True, null=True)
    image_5 = models.ImageField(upload_to='assets/products', blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product_name)
        if not self.category_slug:
            self.category_slug = slugify(self.category)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.product_name}"

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    bid_amount = models.FloatField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.product_name} x {self.quantity}"

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.product.product_name}"

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey('Profile.Address', on_delete=models.SET_NULL, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.FloatField()
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name} in Order #{self.order.id}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    response_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.subject or 'No Subject'}"

class InventoryDashboard(models.Model):
    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventory"
        managed = False