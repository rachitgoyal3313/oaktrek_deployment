# chatbot/ai_chat.py
import requests
import json
import logging
from django.conf import settings
from datetime import datetime
from Store.models import Order, Product, Cart, Wishlist
from Profile.models import User

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def generate_chat_response(user: User, message: str) -> str:
    """
    Generate contextual chatbot responses using user-specific data
    """
    try:
        # Get comprehensive user context
        context = build_chat_context(user, message)
        
        # Prepare system prompt
        system_prompt = f"""
        You are Rachat.ai, the AI assistant for OakTrek Shoes. Respond to customer inquiries using this context:
        
        {json.dumps(context, cls=DateTimeEncoder)}
        
        Response Guidelines:
        1. Be conversational and friendly
        2. Reference order/cart data when relevant
        3. Suggest products from wishlist/cart
        4. Keep responses under 3 sentences
        5. For order status, show recent orders first
        6. Use simple markdown formatting (*bold*, _italic_)
        7. Never disclose personal user data
        """

        # Use OpenRouter's API with Mistral (or other preferred model)
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            },
            timeout=10
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        return fallback_response()

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return fallback_response()

def build_chat_context(user: User, message: str) -> dict:
    """Build structured context from user data"""
    user_context = get_user_context(user)
    shopping_data = {
        "orders": get_order_context(user),
        "cart": get_cart_context(user),
        "wishlist": get_wishlist_context(user)
    }
    product_catalog = get_product_catalog()
    
    return {
        "user_profile": user_context,
        "shopping_data": shopping_data,
        "product_catalog": product_catalog,
        "last_message": message
    }

def get_user_context(user: User) -> dict:
    return {
        "name": user.get_full_name() or user.username,
        "email": user.email,
        "phone": user.phone_number,
        "joined_date": user.date_joined.strftime("%Y-%m-%d")
    }

def get_order_context(user: User) -> list:
    orders = list(Order.objects.filter(user=user)
                .order_by('-order_date')
                .values('id', 'total_amount', 'order_date', 'payment_status')[:5])
    
    # Convert to JSON-serializable format
    return json.loads(json.dumps(orders, cls=DateTimeEncoder))

def get_cart_context(user: User) -> dict:
    cart_items = list(Cart.objects.filter(user=user)
                     .select_related('product')
                     .values('product__id', 'product__product_name', 'quantity', 'product__price'))
    
    cart_data = {
        "item_count": len(cart_items),
        "total_value": sum(item['product__price'] * item['quantity'] for item in cart_items),
        "items": cart_items
    }
    
    # Convert to JSON-serializable format
    return json.loads(json.dumps(cart_data, cls=DateTimeEncoder))

def get_wishlist_context(user: User) -> list:
    wishlist_items = list(Wishlist.objects.filter(user=user)
               .values_list('product__product_name', flat=True))
    
    # Convert to JSON-serializable format
    return json.loads(json.dumps(list(wishlist_items), cls=DateTimeEncoder))

def get_product_catalog() -> list:
    products = list(Product.objects.all()
               .values('id', 'product_name', 'price', 'category', 'rating')[:50])
    
    # Convert to JSON-serializable format
    return json.loads(json.dumps(products, cls=DateTimeEncoder))

def fallback_response() -> str:
    return """Hi there! I'm currently having trouble accessing that information. 
Please try again later or contact our support team at support@oaktrek.com."""
