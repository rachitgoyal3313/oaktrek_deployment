from datetime import datetime
import random
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oaktrek_v2.settings')

django.setup()

from django.core.management.base import BaseCommand
from Store.models import Product, Review, Cart, Wishlist, Order
from Profile.models import User, Address

# List of dummy product data
products_data = [
    # Men's Everyday Sneakers
    {"product_name": "Tree Runner Go", "category": "Everyday Sneakers", "gender": "Male", "price": 120.00, "image_1": "1image1.png", "image_2": "1image2.png", "image_3": "1image3.png", "image_4": "1image4.png", "image_5": "1image5.png"},
    {"product_name": "Tree Runner Classic", "category": "Everyday Sneakers", "gender": "Male", "price": 98.00, "image_1": "2image1.png", "image_2": "2image2.png", "image_3": "2image3.png", "image_4": "2image4.png", "image_5": "2image5.png"},
    {"product_name": "Wool Runner", "category": "Everyday Sneakers", "gender": "Male", "price": 110.00, "image_1": "3image1.png", "image_2": "3image2.png", "image_3": "3image3.png", "image_4": "3image4.png", "image_5": "3image5.png"},
    {"product_name": "Tree Runner Pro", "category": "Everyday Sneakers", "gender": "Male", "price": 115.00, "image_1": "4image1.png", "image_2": "4image2.png", "image_3": "4image3.png", "image_4": "4image4.png", "image_5": "4image5.png"},
    {"product_name": "Cloud Walker", "category": "Everyday Sneakers", "gender": "Male", "price": 130.00, "image_1": "5image1.png", "image_2": "5image2.png", "image_3": "5image3.png", "image_4": "5image4.png", "image_5": "5image5.png"},
    {"product_name": "Eco Step", "category": "Everyday Sneakers", "gender": "Male", "price": 105.00, "image_1": "6image1.png", "image_2": "6image2.png", "image_3": "6image3.png", "image_4": "6image4.png", "image_5": "6image5.png"},
    {"product_name": "Eco Glide", "category": "Everyday Sneakers", "gender": "Male", "price": 108.00, "image_1": "7image1.png", "image_2": "7image2.png", "image_3": "7image3.png", "image_4": "7image4.png", "image_5": "7image5.png"},
    {"product_name": "Zen Walker", "category": "Everyday Sneakers", "gender": "Male", "price": 125.00, "image_1": "8image1.png", "image_2": "8image2.png", "image_3": "8image3.png", "image_4": "8image4.png", "image_5": "8image5.png"},
    # Men's Active Shoes
    {"product_name": "Tree Dasher 2", "category": "Active Shoes", "gender": "Male", "price": 135.00, "image_1": "9image1.png", "image_2": "9image2.png", "image_3": "9image3.png", "image_4": "9image4.png", "image_5": "9image5.png"},
    {"product_name": "Tree Flyer", "category": "Active Shoes", "gender": "Male", "price": 160.00, "image_1": "10image1.png", "image_2": "10image2.png", "image_3": "10image3.png", "image_4": "10image4.png", "image_5": "10image5.png"},
    {"product_name": "Power Sprint", "category": "Active Shoes", "gender": "Male", "price": 140.00, "image_1": "11image1.png", "image_2": "11image2.png", "image_3": "11image3.png", "image_4": "11image4.png", "image_5": "11image5.png"},
    {"product_name": "Flex Runner", "category": "Active Shoes", "gender": "Male", "price": 150.00, "image_1": "12image1.png", "image_2": "12image2.png", "image_3": "12image3.png", "image_4": "12image4.png", "image_5": "12image5.png"},
    {"product_name": "Speed Glide", "category": "Active Shoes", "gender": "Male", "price": 145.00, "image_1": "13image1.png", "image_2": "13image2.png", "image_3": "13image3.png", "image_4": "13image4.png", "image_5": "13image5.png"},
    {"product_name": "Urban Runner", "category": "Active Shoes", "gender": "Male", "price": 155.00, "image_1": "14image1.png", "image_2": "14image2.png", "image_3": "14image3.png", "image_4": "14image4.png", "image_5": "14image5.png"},
    # Men's Water Repellent Shoes
    {"product_name": "Mizzle Runner", "category": "Water Repellent Shoes", "gender": "Male", "price": 125.00, "image_1": "15image1.png", "image_2": "15image2.png", "image_3": "15image3.png", "image_4": "15image4.png", "image_5": "15image5.png"},
    {"product_name": "Storm Shield", "category": "Water Repellent Shoes", "gender": "Male", "price": 140.00, "image_1": "16image1.png", "image_2": "16image2.png", "image_3": "16image3.png", "image_4": "16image4.png", "image_5": "16image5.png"},
    {"product_name": "Aqua Guard", "category": "Water Repellent Shoes", "gender": "Male", "price": 135.00, "image_1": "17image1.png", "image_2": "17image2.png", "image_3": "17image3.png", "image_4": "17image4.png", "image_5": "17image5.png"},
    {"product_name": "Storm Chaser", "category": "Water Repellent Shoes", "gender": "Male", "price": 145.00, "image_1": "18image1.png", "image_2": "18image2.png", "image_3": "18image3.png", "image_4": "18image4.png", "image_5": "18image5.png"},
    # Men's Hiking Shoes
    {"product_name": "Trail Runner SWT", "category": "Hiking Shoes", "gender": "Male", "price": 150.00, "image_1": "19image1.avif", "image_2": "19image2.avif", "image_3": "19image3.avif", "image_4": "19image4.avif", "image_5": "19image5.avif"},
    {"product_name": "Rugged Explorer", "category": "Hiking Shoes", "gender": "Male", "price": 155.00, "image_1": "20image1.avif", "image_2": "20image2.avif", "image_3": "20image3.avif", "image_4": "20image4.avif", "image_5": "20image5.avif"},
    # Men's Slip Ons
    {"product_name": "Tree Lounger", "category": "Slip Ons", "gender": "Male", "price": 98.00, "image_1": "21image1.png", "image_2": "21image2.png", "image_3": "21image3.png", "image_4": "21image4.png", "image_5": "21image5.png"},
    {"product_name": "Cloud Loafer", "category": "Slip Ons", "gender": "Male", "price": 105.00, "image_1": "22image1.png", "image_2": "22image2.png", "image_3": "22image3.png", "image_4": "22image4.png", "image_5": "22image5.png"},
    {"product_name": "Breeze Slip", "category": "Slip Ons", "gender": "Male", "price": 100.00, "image_1": "23image1.png", "image_2": "23image2.png", "image_3": "23image3.png", "image_4": "23image4.png", "image_5": "23image5.png"},
    # Women's Everyday Sneakers
    {"product_name": "Tree Runner Go Women's", "category": "Everyday Sneakers", "gender": "Female", "price": 120.00, "image_1": "24image1.png", "image_2": "24image2.png", "image_3": "24image3.png", "image_4": "24image4.png", "image_5": "24image5.png"},
    {"product_name": "Tree Runner Classic Women's", "category": "Everyday Sneakers", "gender": "Female", "price": 98.00, "image_1": "25image1.png", "image_2": "25image2.png", "image_3": "25image3.png", "image_4": "25image4.png", "image_5": "25image5.png"},
    {"product_name": "Wool Breeze", "category": "Everyday Sneakers", "gender": "Female", "price": 115.00, "image_1": "26image1.png", "image_2": "26image2.png", "image_3": "26image3.png", "image_4": "26image4.png", "image_5": "26image5.png"},
    {"product_name": "Feather Glide", "category": "Everyday Sneakers", "gender": "Female", "price": 125.00, "image_1": "27image1.png", "image_2": "27image2.png", "image_3": "27image3.png", "image_4": "27image4.png", "image_5": "27image5.png"},
    {"product_name": "Cloud Walker Women's", "category": "Everyday Sneakers", "gender": "Female", "price": 130.00, "image_1": "28image1.jpg", "image_2": "28image2.jpg", "image_3": "28image3.jpg", "image_4": "28image4.jpg", "image_5": "28image5.jpg"},
    # Women's Active Shoes
    {"product_name": "Tree Dasher 2 Women's", "category": "Active Shoes", "gender": "Female", "price": 135.00, "image_1": "29image1.png", "image_2": "29image2.png", "image_3": "29image3.png", "image_4": "29image4.png", "image_5": "29image5.png"},
    {"product_name": "Tree Sprinter", "category": "Active Shoes", "gender": "Female", "price": 140.00, "image_1": "30image1.png", "image_2": "30image2.png", "image_3": "30image3.png", "image_4": "30image4.png", "image_5": "30image5.png"},
    {"product_name": "Power Glide Women's", "category": "Active Shoes", "gender": "Female", "price": 145.00, "image_1": "31image1.png", "image_2": "31image2.png", "image_3": "31image3.png", "image_4": "31image4.png", "image_5": "31image5.png"},
    # Women's Ballet Flats
    {"product_name": "Tree Breezer", "category": "Ballet Flats", "gender": "Female", "price": 98.00, "image_1": "32image1.avif", "image_2": "32image2.avif", "image_3": "32image3.avif", "image_4": "32image4.avif", "image_5": "32image5.avif"},
    {"product_name": "Cloud Ballet", "category": "Ballet Flats", "gender": "Female", "price": 105.00, "image_1": "33image1.avif", "image_2": "33image2.avif", "image_3": "33image3.avif", "image_4": "33image4.avif", "image_5": "33image5.avif"},
    {"product_name": "Dew Soft", "category": "Ballet Flats", "gender": "Female", "price": 102.00, "image_1": "34image1.avif", "image_2": "34image2.avif", "image_3": "34image3.avif", "image_4": "34image4.avif", "image_5": "34image5.avif"},
    {"product_name": "Luna Slidr", "category": "Ballet Flats", "gender": "Female", "price": 102.00, "image_1": "34_1image1.avif", "image_2": "34_1image2.avif", "image_3": "34_1image3.avif", "image_4": "34_1image4.avif", "image_5": "34_1image5.avif"},
    {"product_name": "Dawn Hoppr", "category": "Ballet Flats", "gender": "Female", "price": 102.00, "image_1": "34_2image1.avif", "image_2": "34_2image2.avif", "image_3": "34_2image3.avif", "image_4": "34_2image4.avif", "image_5": "34_2image5.avif"},
    {"product_name": "Leaf Skippr", "category": "Ballet Flats", "gender": "Female", "price": 102.00, "image_1": "34_3image1.avif", "image_2": "34_3image2.avif", "image_3": "34_3image3.avif", "image_4": "34_3image4.avif", "image_5": "34_3image5.avif"},
    # Women's Slip Ons
    {"product_name": "Sun Breeze", "category": "Slip Ons", "gender": "Female", "price": 110.00, "image_1": "35image1.avif", "image_2": "35image2.avif", "image_3": "35image3.avif", "image_4": "35image4.avif", "image_5": "35image5.avif"},
    {"product_name": "Cloud Floatr", "category": "Slip Ons", "gender": "Female", "price": 110.00, "image_1": "35_1image1.avif", "image_2": "35_1image2.avif", "image_3": "35_1image3.avif", "image_4": "35_1image4.avif", "image_5": "35_1image5.avif"},
    {"product_name": "Wave Glyde", "category": "Slip Ons", "gender": "Female", "price": 110.00, "image_1": "35_2image1.avif", "image_2": "35_2image2.avif", "image_3": "35_2image3.avif", "image_4": "35_2image4.avif", "image_5": "35_2image5.avif"},
    # Women's Hiking Shoes
    {"product_name": "Mountain Trekker", "category": "Hiking Shoes", "gender": "Female", "price": 160.00, "image_1": "36image1.png", "image_2": "36image2.png", "image_3": "36image3.png", "image_4": "36image4.png", "image_5": "36image5.png"},
    {"product_name": "Wild Trail", "category": "Hiking Shoes", "gender": "Female", "price": 145.00, "image_1": "37image1.png", "image_2": "37image2.png", "image_3": "37image3.png", "image_4": "37image4.png", "image_5": "37image5.png"},
    {"product_name": "Summit Seeker", "category": "Hiking Shoes", "gender": "Female", "price": 170.00, "image_1": "38image1.png", "image_2": "38image2.png", "image_3": "38image3.png", "image_4": "38image4.png", "image_5": "38image5.png"},
    {"product_name": "Urban Stride", "category": "Everyday Sneakers", "gender": "Male", "price": 110.00, "image_1": "39image1.png", "image_2": "39image2.png", "image_3": "39image3.jpg", "image_4": "39image4.png", "image_5": "39image5.jpg"},
    {"product_name": "Eco Trek", "category": "Everyday Sneakers", "gender": "Male", "price": 112.00, "image_1": "40image1.png", "image_2": "40image2.png", "image_3": "40image3.png", "image_4": "40image4.png", "image_5": "40image5.png"},
    # Additional Men's Active Shoes
    {"product_name": "Turbo Dash", "category": "Active Shoes", "gender": "Male", "price": 148.00, "image_1": "41image1.png", "image_2": "41image2.png", "image_3": "41image3.png", "image_4": "41image4.png", "image_5": "41image5.png"},
    {"product_name": "Aero Sprint", "category": "Active Shoes", "gender": "Male", "price": 155.00, "image_1": "42image1.png", "image_2": "42image2.png", "image_3": "42image3.png", "image_4": "42image4.png", "image_5": "42image5.png"},
    # Additional Men's Water Repellent Shoes
    {"product_name": "Rain Shield", "category": "Water Repellent Shoes", "gender": "Male", "price": 130.00, "image_1": "43image1.png", "image_2": "43image2.png", "image_3": "43image3.png", "image_4": "43image4.png", "image_5": "43image5.png"},
    {"product_name": "Aqua Trek", "category": "Water Repellent Shoes", "gender": "Male", "price": 138.00, "image_1": "44image1.png", "image_2": "44image2.png", "image_3": "44image3.png", "image_4": "44image4.png", "image_5": "44image5.png"},
    # Additional Men's Hiking Shoes
    {"product_name": "Trail Master", "category": "Hiking Shoes", "gender": "Male", "price": 165.00, "image_1": "45image1.png", "image_2": "45image2.png", "image_3": "45image3.png", "image_4": "45image4.png", "image_5": "45image5.jpg"},
    {"product_name": "Summit Climber", "category": "Hiking Shoes", "gender": "Male", "price": 170.00, "image_1": "46image1.png", "image_2": "46image2.png", "image_3": "46image3.png", "image_4": "46image4.png", "image_5": "46image5.png"},
    # Additional Women's Everyday Sneakers
    {"product_name": "Breeze Runner", "category": "Everyday Sneakers", "gender": "Female", "price": 118.00, "image_1": "47image1.png", "image_2": "47image2.png", "image_3": "47image3.png", "image_4": "47image4.png", "image_5": "47image5.png"},
    {"product_name": "Eco Glide Women's", "category": "Everyday Sneakers", "gender": "Female", "price": 122.00, "image_1": "48image1.png", "image_2": "48image2.png", "image_3": "48image3.png", "image_4": "48image4.png", "image_5": "48image5.png"},
    # Additional Women's Active Shoes
    {"product_name": "Sky Sprint", "category": "Active Shoes", "gender": "Female", "price": 142.00, "image_1": "49image1.png", "image_2": "49image2.png", "image_3": "49image3.png", "image_4": "49image4.png", "image_5": "49image5.png"},
    {"product_name": "Aero Glide Women's", "category": "Active Shoes", "gender": "Female", "price": 150.00, "image_1": "50image1.png", "image_2": "50image2.png", "image_3": "50image3.png", "image_4": "50image4.png", "image_5": "50image5.png"}
]

# Sample user data to create users
users_data = [
    {"username": "user1", "email": "user1@example.com", "first_name": "John", "last_name": "Doe", "password": "password123"},
    {"username": "user2", "email": "user2@example.com", "first_name": "Jane", "last_name": "Smith", "password": "password123"},
    {"username": "user3", "email": "user3@example.com", "first_name": "Robert", "last_name": "Johnson", "password": "password123"},
    {"username": "user4", "email": "user4@example.com", "first_name": "Emily", "last_name": "Brown", "password": "password123"},
    {"username": "user5", "email": "user5@example.com", "first_name": "Michael", "last_name": "Wilson", "password": "password123"}
]

def seed_database():
    print("Starting database seeding...")
    
    print("Clearing existing data...")
    # Clear existing data
    try:
        Product.objects.all().delete()
        Review.objects.all().delete()
        Cart.objects.all().delete()
        Wishlist.objects.all().delete()
        Order.objects.all().delete()
        Address.objects.all().delete()
        User.objects.all().delete()  # Be cautious with this in production
    except Exception as e:
        print(f"Error clearing data: {e}")

    print("Creating users...")
    # Create users
    users = []
    for user_data in users_data:
        password = user_data.pop("password")
        user, created = User.objects.get_or_create(
            username=user_data["username"],
            defaults=user_data
        )
        if created:
            user.set_password(password)
            user.save()
        users.append(user)
    
    print("Adding products...")
    # Add products
    created_products = []
    for product_data in products_data:
        if "rating" not in product_data:
            product_data["rating"] = round(random.uniform(3.0, 5.0), 1)
        
        product = Product.objects.create(**product_data)
        created_products.append(product)
    
    print("Adding reviews...")
    # Create reviews
    for product in random.sample(created_products, min(30, len(created_products))):
        for _ in range(random.randint(1, 3)):
            user = random.choice(users)
            rating = random.randint(3, 5)
            comments = [
                "Great product, very comfortable!",
                "Love the design and quality.",
                "Fits perfectly and looks stylish.",
                "Excellent purchase, highly recommend!",
                "Good value for money.",
                "Very comfortable for everyday wear.",
                "The quality exceeded my expectations.",
                "Perfect fit and great style."
            ]
            
            Review.objects.create(
                user=user,
                product=product,
                rating=rating,
                comment=random.choice(comments)
            )
    
    print("Adding cart items...")
    # Create cart items
    for user in users:
        for _ in range(random.randint(0, 3)):
            product = random.choice(created_products)
            quantity = random.randint(1, 2)
            
            cart_item, created = Cart.objects.get_or_create(
                user=user,
                product=product,
                defaults={"quantity": quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
    
    print("Adding wishlist items...")
    # Create wishlist items
    for user in users:
        for product in random.sample(created_products, random.randint(0, 5)):
            Wishlist.objects.get_or_create(
                user=user,
                product=product
            )
    
    print("Creating orders...")
    # Create orders
    for user in users:
        for _ in range(random.randint(0, 2)):
            # Create address
            address, _ = Address.objects.get_or_create(
                user=user,
                defaults={
                    "name": f"{user.first_name} {user.last_name}",
                    "street": f"{random.randint(100, 999)} Main St",
                    "city": "Cityville",
                    "state": "ST",
                    "zipcode": f"{random.randint(10000, 99999)}",
                    "is_default": True
                }
            )
            
            # Create order with random products
            order_products = random.sample(created_products, random.randint(1, 3))
            total_amount = sum(product.price for product in order_products)
            
            order = Order.objects.create(
                user=user,
                address=address,
                total_amount=total_amount
            )
    
    print(f"Successfully seeded database with:")
    print(f"- {User.objects.count()} users")
    print(f"- {Product.objects.count()} products")
    print(f"- {Review.objects.count()} reviews")
    print(f"- {Cart.objects.count()} cart items")
    print(f"- {Wishlist.objects.count()} wishlist items")
    print(f"- {Order.objects.count()} orders")
    print(f"- {Address.objects.count()} addresses")

# Create a management command
class Command(BaseCommand):
    help = 'Seed the database with users, products, reviews, carts, wishlists, orders, and addresses'

    def handle(self, *args, **options):
        seed_database()

if __name__ == "__main__":
    seed_database()