# chatbot/views.py
import json
from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ChatMessage
from Store.models import Order, Cart, Wishlist
from .ai_chat import generate_chat_response

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

@login_required
def chat_interface(request):
    """Render the chat interface"""
    return render(request, 'chat.html')

def get_order_context(user):
    """Get user's order history in JSON-serializable format"""
    orders = list(Order.objects.filter(user=user)
                  .order_by('-order_date')
                  .values('id', 'total_amount', 'order_date', 'payment_status')[:3])
    
    # Convert to JSON-serializable format using custom encoder
    return json.loads(json.dumps(orders, cls=DateTimeEncoder))

def get_cart_context(user):
    """Get user's cart items in JSON-serializable format"""
    cart_items = list(Cart.objects.filter(user=user)
                      .select_related('product')
                      .values('product__product_name', 'quantity', 'product__price'))
    
    wishlist_items = list(Wishlist.objects.filter(user=user)
                         .values_list('product__product_name', flat=True))
    
    cart_data = {
        'cart_items': cart_items,
        'wishlist_items': wishlist_items,
        'total_items': len(cart_items),
        'total_value': sum(item['product__price'] * item['quantity'] for item in cart_items)
    }
    
    # Convert to JSON-serializable format using custom encoder
    return json.loads(json.dumps(cart_data, cls=DateTimeEncoder))

@require_POST
@login_required
def send_message(request):
    """Process user message and generate AI response"""
    user_message = request.POST.get('message', '')
    user = request.user
    
    # Get context data and ensure it's JSON serializable
    order_context = get_order_context(user)
    cart_context = get_cart_context(user)
    
    # Save user message
    ChatMessage.objects.create(
        user=user,
        message=user_message,
        is_bot=False,
        order_context=order_context,
        cart_context=cart_context
    )
    
    # Generate bot response
    bot_response = generate_chat_response(user, user_message)
    
    # Save bot response
    ChatMessage.objects.create(
        user=user,
        message=bot_response,
        is_bot=True
    )
    
    return JsonResponse({'response': bot_response})

@login_required
def clear_chat(request):
    """Clear all chat messages for the current user"""
    if request.method == 'POST':
        ChatMessage.objects.filter(user=request.user).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


@login_required
def chat(request):
    return render(request, 'chat.html')