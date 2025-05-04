import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oaktrek_v2.settings')
django.setup()

from Store.models import Product

media_dir = r'C:\Users\goyal\Desktop\oaktrek v2_2\oaktrek_v2\media\assets\products'
image_files = set(os.listdir(media_dir))

for product in Product.objects.all():
    if product.image_1:
        filename = os.path.basename(product.image_1.name)
        if filename in image_files:
            product.image_1 = f"assets/products/{filename}"
            product.image_2 = f"assets/products/{filename}"
            product.image_3 = f"assets/products/{filename}"
            product.image_4 = f"assets/products/{filename}"
            product.image_5 = f"assets/products/{filename}"
            product.save()
            print(f"Updated {product.product_name}: image_1 = {product.image_1}")