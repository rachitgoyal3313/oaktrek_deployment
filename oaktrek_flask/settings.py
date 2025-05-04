# flask_inventory_api/settings.py
import os
import sys
import django

# Add Django project to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oaktrek_v2.settings')
django.setup()
