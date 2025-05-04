from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, Order, OrderItem, Review, ContactMessage
from Profile.models import Address
from django.utils.text import slugify
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.conf import settings
from django import forms
from django.core.mail import send_mail
from .models import ContactForm
from django.db.models import Q, Avg
import re
import uuid
from django.core.paginator import Paginator
import requests
import json
import logging
from .ai_service import generate_ai_response
from .email_service import send_email_response
import razorpay
import random
from django.http import JsonResponse
from django.utils import timezone
from .services.inventory_service import InventoryService

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'index.html', {
        'MEDIA_URL': settings.MEDIA_URL,
    })

def normalize_gender_query(query):
    query = query.lower()

    male_keywords = ['men', "men's", 'mens', 'man', 'male', 'boys', 'dudes', 'queer','rachit', 'divyansh', 'pushkar', 'handsome']
    female_keywords = ['women', "women's", 'womens', 'lady', 'ladies', 'female', 'girls', 'gay', 'bi', 'queer', 'abhinav', 'sexy' ]
    unisex_keywords = ['unisex', 'all', 'any', 'everyone', 'nonbinary', 'pan', 'fab', 'slay']

    for word in male_keywords:
        if re.search(rf'\b{re.escape(word)}\b', query):
            return 'Male'
    for word in female_keywords:
        if re.search(rf'\b{re.escape(word)}\b', query):
            return 'Female'
    for word in unisex_keywords:
        if re.search(rf'\b{re.escape(word)}\b', query):
            return 'Unisex'

    return None

def search(request):
    """
    Search view that handles product search functionality
    """
    query = None
    results = None

    if 'q' in request.GET:
        query = request.GET.get('q').strip()
        if query:
            normalized_gender = normalize_gender_query(query)

            # Build search filter
            filters = (
                Q(category__icontains=query) |
                Q(product_name__icontains=query)
            )

            if normalized_gender:
                filters |= Q(gender__iexact=normalized_gender)
            else:
                filters |= Q(gender__icontains=query)

            results = Product.objects.filter(filters)

    products_with_images = []
    if results:
        for product in results:
            product_images = [img for img in [
                product.image_1, product.image_2,
                product.image_3, product.image_4, product.image_5
            ] if img]

            products_with_images.append({
                'product': product,
                'images': product_images
            })

    context = {
        'query': query,
        'results': results,
        'products_with_images': products_with_images,
        'is_search_results': True,
    }

    return render(request, 'search_results.html', context)

def sustainability(request):
    return render(request, 'sustainability.html')

def stores(request):
    return render(request, 'stores.html')

def coming_soon(request):
    return render(request, "coming_soon.html")

def products_cat_view(request, gender, collection_name):
    normalized_gender = gender.lower()
    category = None
    gender = None
    if normalized_gender in ["male", "mens", "men's", "men"]:
        gender = "Male"
    elif normalized_gender in ["Women", "Womens", "Wommen's", "women"]:
        gender = "Female"
        category = "Women"

    products = Product.objects.filter(gender=gender, category_slug = collection_name)

    category = products[1].category
    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'relevance':
        # For random ordering in Django
        products = products.order_by('?')
    
    context = {
        'products': products,
        'collection_name': collection_name,  
        'original_collection_name': collection_name,  
        'product_category': category, 
        "sizes": [8, 9, 10, 11, 12]
    }

    return render(request, 'products.html', context)

def products_view(request, collection_name):
    normalized_collection_name = collection_name.lower()
    category = None
    if normalized_collection_name in ["male", "mens", "men's", "men"]:
        collection_name = "Men"
        products = Product.objects.filter(gender="Male")
        category = "Men"
    elif normalized_collection_name in ["Women", "Womens", "Wommen's", "women"]:
        collection_name = "Women"
        category = "Women"
        products = Product.objects.filter(gender="Female")
    else:
         products = Product.objects.filter(category_slug=collection_name)
         category = products[1].category

    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'relevance':
        # For random ordering in Django
        products = products.order_by('?')
    
    context = {
        'products': products,
        'collection_name': collection_name,  
        'original_collection_name': collection_name,  
        'product_category': category, 
        "sizes": [8, 9, 10, 11, 12]
    }
    return render(request, 'products.html', context)

def product_page_view(request, collection_name, product_slug):
    product = None
    if collection_name.lower() in ["male", "mens", "men's", "men"]:
        gender = "Male"
        product = get_object_or_404(Product, gender=gender, slug=product_slug)
    elif collection_name.lower() in ["Women", "Womens", "Wommen's", "women"]:
        gender = "Female"
        product = get_object_or_404(Product, gender=gender, slug=product_slug)
    else:
        product = get_object_or_404(Product, category_slug=collection_name, slug=product_slug)

    product_images = []
    for img in [product.image_1, product.image_2, product.image_3, product.image_4, product.image_5]:
        if img:
            product_images.append(img)

    reviews_list = product.reviews.all().order_by('-created_at')
    paginator = Paginator(reviews_list, 5)  # Show 5 reviews per page
    page = request.GET.get('page')
    reviews = paginator.get_page(page)
    rating = product.rating
    stars = []
    for i in range(1, 6):
        if i <= rating:
            stars.append("fas fa-star")  # full star
        elif i - rating <= 0.5:
            stars.append("fas fa-star-half-alt")  # half star
        else:
            stars.append("far fa-star")

    context = {
        "sizes": [8, 9, 10, 11, 12],
        'collection_name': collection_name,  # For URL consistency
        'product': product,
        'product_images': product_images,
        'reviews': reviews,
        'star_range': stars
    }

    return render(request, 'product_page.html', context)

@login_required
def add_review(request, collection_name, product_slug):
    product = None
    if collection_name.lower() in ["male", "mens", "men's", "men"]:
        gender = "Male"
        product = get_object_or_404(Product, gender=gender, slug=product_slug)
    elif collection_name.lower() in ["women", "womens", "women's", "women"]:
        gender = "Female"
        product = get_object_or_404(Product, gender=gender, slug=product_slug)
    else:
        product = get_object_or_404(Product, category_slug=collection_name, slug=product_slug)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        
        # Check if user already reviewed this product
        existing_review = Review.objects.filter(user=request.user, product=product).first()
        
        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
        else:
            # Create new review
            Review.objects.create(
                user=request.user,
                product=product,
                rating=rating,
                comment=comment
            )
            
        # Update product rating
        all_ratings = product.reviews.all().values_list('rating', flat=True)
        if all_ratings:
            product.rating = sum(all_ratings) / len(all_ratings)
            product.save()
            
    return redirect('product_page', collection_name=collection_name, product_slug=product_slug)

def moonshot(request):
    return render(request, 'moonshot.html')

def mothernature(request):
    return render(request, 'moonshot.html')

def adidasxoaktrek(request):
    return render(request, 'adidasxoaktrek.html')

def bcorp(request):
    return render(request, 'bcorp.html')

def carbonFootprint(request):
    return render(request, 'carbonoffsets.html')

def oaktrek_help(request):
    user = request.user
    if request.method == 'POST':
        # Extract form data
        name = request.POST.get('name')
        email = user.email
        subject = request.POST.get('subject', '')
        message = request.POST.get('message')
        
        # Save message to database
        contact = ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        # Get user's order details if they exist
        order_details = ""
        if request.user.is_authenticated:
            user_orders = Order.objects.filter(user=request.user).order_by('-order_date')[:5]  # Get last 5 orders
            
            if user_orders:
                order_details = "Recent order history:\n"
                for order in user_orders:
                    order_details += f"- Order #{order.id} (Date: {order.order_date.strftime('%Y-%m-%d')}): ${order.total_amount}\n"
                    items = OrderItem.objects.filter(order=order)
                    for item in items:
                        product_name = item.product.product_name if item.product else "Unknown Product"
                        order_details += f"  * {item.quantity} x {product_name} (${item.price})\n"
        
        # Generate AI response
        ai_response = generate_ai_response(name, email, message, order_details)
        
        # Send email response using the HTML template
        send_email_response(name, email, subject, ai_response)
        
        # Mark as responded
        contact.response_sent = True
        contact.save()
        
        # Redirect or render success message
        return render(request, 'oaktrek_help.html', {'form_submitted': True})
    
    return render(request, 'oaktrek_help.html')

def faq(request):
    return render(request, 'faq.html')

def returns(request):
    return render(request, 'returns.html')

def aboutUs(request):
    return render(request, 'about_us.html')

def our_story(request):
    return render(request, 'our_story.html')

def our_materials(request):
    return render(request, 'our_materials.html')

def sustainability(request):
    return render(request, 'sustainability.html')

def regenerative(request):
    return render(request, 'regenerative.html')

def renewable(request):
    return render(request, 'renewable.html')

def terms(request):
    return render(request, 'terms.html')

def responsibleEnergy(request):
    return render(request, 'responsibleenergy.html')

@login_required
def cart_view(request):
    user = request.user

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        selected_color = request.POST.get('selected_color')
        selected_size = request.POST.get('selected_size')

        # For actions like increase/decrease quantity
        if action in ['increase', 'decrease']:
            product = get_object_or_404(Product, id=product_id)
            cart_item, created = Cart.objects.get_or_create(user=user, product=product)

            if action == 'increase':
                cart_item.quantity += 1
                cart_item.save()
            elif action == 'decrease':
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
        # For adding to cart
        else:
            # Server-side validation as a backup
            if not selected_size:
                messages.error(request, "Please select a size before adding to cart")
                product = get_object_or_404(Product, id=product_id)
                return redirect('product_page', collection_name=product.category_slug, product_slug=product.slug)

            product = get_object_or_404(Product, id=product_id)
            cart_item, created = Cart.objects.get_or_create(user=user, product=product)
            
            # If it's a new item, set quantity to 1, otherwise increment
            if not created:
                cart_item.quantity += 1
            cart_item.save()

        return redirect('cart')

    # GET request
    cart_items = Cart.objects.filter(user=user).select_related('product')
    total = sum((item.bid_amount if item.bid_amount is not None else item.product.price) * item.quantity for item in cart_items)
    tax = total * 0.28
    context = {
        'cart_items': cart_items,
        'tax': tax,
        'subtotal': total,
        'total': total + tax,
    }
    return render(request, 'cart.html', context)

def join(request):
    return render(request, "join.html")

def error_page(request):
    return render(request, "404.html")

@login_required
@transaction.atomic
def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user).select_related('product')
    
    if not cart_items.exists():
        return redirect('cart')

    # Calculate amounts, using bid_amount for auction items
    subtotal = sum((item.bid_amount if item.bid_amount is not None else item.product.price) * item.quantity for item in cart_items)
    tax = subtotal * 0.28
    total_amount = subtotal + tax

    # Prepare cart items with computed totals for template
    cart_items_with_totals = [
        {
            'item': item,
            'total': (item.bid_amount if item.bid_amount is not None else item.product.price) * item.quantity
        }
        for item in cart_items
    ]

    # Log the calculations for debugging
    logger.info(f"Checkout for user {user.username}:")
    for item in cart_items:
        price_used = item.bid_amount if item.bid_amount is not None else item.product.price
        logger.info(f"Item: {item.product.product_name}, Quantity: {item.quantity}, Price: {price_used}, Bid Amount: {item.bid_amount}, Total: {price_used * item.quantity}")
    logger.info(f"Subtotal: {subtotal}, Tax: {tax}, Total: {total_amount}")

    if request.method == 'POST':
        # Payment verification and order processing
        address_id = request.POST.get('address_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Validate address
        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            logger.error(f"Invalid address_id: {address_id}")
            return render(request, 'checkout.html', {
                'error': 'Invalid address selected.',
                'cart_items': cart_items_with_totals,
                'tax': tax,
                'subtotal': subtotal,
                'total': total_amount,
                'addresses': user.addresses.all(),
                'razorpay_order_id': razorpay_order_id,
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            })

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Verify payment
        if razorpay_payment_id and razorpay_order_id:
            if razorpay_signature:
                # Try signature verification (for UPI ID/intent payments)
                params_dict = {
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_signature': razorpay_signature
                }
                try:
                    client.utility.verify_payment_signature(params_dict)
                    logger.info(f"Payment verified via signature: {razorpay_payment_id}")
                except razorpay.errors.SignatureVerificationError as e:
                    logger.error(f"Signature verification failed: {str(e)}")
                    # Fallback to payment status check for QR code payments
                    try:
                        payment = client.payment.fetch(razorpay_payment_id)
                        if payment['status'] == 'captured' and payment['order_id'] == razorpay_order_id:
                            logger.info(f"QR code payment verified via API: {razorpay_payment_id}")
                        else:
                            logger.error(f"Payment not captured: {payment['status']}")
                            return render(request, 'checkout.html', {
                                'error': 'Payment not completed. Please try again.',
                                'cart_items': cart_items_with_totals,
                                'tax': tax,
                                'subtotal': subtotal,
                                'total': total_amount,
                                'addresses': user.addresses.all(),
                                'razorpay_order_id': razorpay_order_id,
                                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                            })
                    except Exception as e:
                        logger.error(f"Failed to fetch payment: {str(e)}")
                        return render(request, 'checkout.html', {
                            'error': 'Payment verification failed.',
                            'cart_items': cart_items_with_totals,
                            'tax': tax,
                            'subtotal': subtotal,
                            'total': total_amount,
                            'addresses': user.addresses.all(),
                            'razorpay_order_id': razorpay_order_id,
                            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                        })
            else:
                # No signature provided, check payment status directly (for QR code payments)
                try:
                    payment = client.payment.fetch(razorpay_payment_id)
                    if payment['status'] == 'captured' and payment['order_id'] == razorpay_order_id:
                        logger.info(f"QR code payment verified via API: {razorpay_payment_id}")
                    else:
                        logger.error(f"Payment not captured: {payment['status']}")
                        return render(request, 'checkout.html', {
                            'error': 'Payment not completed. Please try again.',
                            'cart_items': cart_items_with_totals,
                            'tax': tax,
                            'subtotal': subtotal,
                            'total': total_amount,
                            'addresses': user.addresses.all(),
                            'razorpay_order_id': razorpay_order_id,
                            'razorpay_key_id': settings.RAZORPAY_KEY_ID
                        })
                except Exception as e:
                    logger.error(f"Failed to fetch payment: {str(e)}")
                    return render(request, 'checkout.html', {
                        'error': 'Payment verification failed.',
                        'cart_items': cart_items_with_totals,
                        'tax': tax,
                        'subtotal': subtotal,
                        'total': total_amount,
                        'addresses': user.addresses.all(),
                        'razorpay_order_id': razorpay_order_id,
                        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    })
        else:
            logger.error("Missing payment_id or order_id")
            return render(request, 'checkout.html', {
                'error': 'Invalid payment details.',
                'cart_items': cart_items_with_totals,
                'tax': tax,
                'subtotal': subtotal,
                'total': total_amount,
                'addresses': user.addresses.all(),
                'razorpay_order_id': razorpay_order_id,
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            })

        # Create order after successful payment verification
        order = Order.objects.create(
            user=user,
            address=address,
            total_amount=total_amount,
            payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            payment_status='Success'
        )

        # Create order items, using bid_amount for auction items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.bid_amount if cart_item.bid_amount is not None else cart_item.product.price
            )

        # Clear cart
        cart_items.delete()
        logger.info(f"Order created: {order.id}")
        return redirect('order_confirmation', order_id=order.id)

    # GET request - show checkout page
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        razorpay_order = client.order.create({
            'amount': int(total_amount * 100),
            'currency': 'INR',
            'payment_capture': '1'
        })
        logger.info(f"Razorpay order created: {razorpay_order['id']}")
    except Exception as e:
        logger.error(f"Failed to create Razorpay order: {str(e)}")
        return render(request, 'checkout.html', {
            'error': 'Failed to initiate payment.',
            'cart_items': cart_items_with_totals,
            'tax': tax,
            'subtotal': subtotal,
            'total': total_amount,
            'addresses': user.addresses.all(),
        })

    context = {
        'cart_items': cart_items_with_totals,
        'tax': tax,
        'subtotal': subtotal,
        'total': total_amount,
        'addresses': user.addresses.all(),
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_amount': int(total_amount * 100),
        'currency': 'INR',
        'merchant_vpa': settings.RAZORPAY_MERCHANT_VPA,
    }

    return render(request, 'checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    """
    View function to display the order confirmation page after a successful checkout.
    
    Args:
        request: The HTTP request object
        order_id: The ID of the order to display confirmation for
    
    Returns:
        Rendered confirmation.html template with order details
    """
    # Get the order or return 404 if not found
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Get all order items related to this order
    order_items = order.items.all().select_related('product')
    
    address = Address.objects.all().filter(user=request.user)

    # Calculate order totals
    subtotal = sum(item.price * item.quantity for item in order_items)
    tax = subtotal * 0.28  # Same tax calculation as in checkout
    total = subtotal + tax
    
    # Generate a formatted order number
    order_number = f"OAK-{order.id}-{uuid.uuid4().hex[:6].upper()}"
    
    # Prepare order items for the template with the required format
    formatted_items = []
    for item in order_items:
        formatted_items.append({
            'name': item.product.product_name,
            'quantity': item.quantity,
            'price': item.price,  # Price is now bid_amount for auction items
            'image': item.product.image_1.url if item.product.image_1 else '',
        })
    
    # Prepare the context for the template
    context = {
        'order_number': order_number,
        'order_items': formatted_items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
        'user': request.user,
        'addresses': address
    }
    
    return render(request, 'confirmation.html', context)

def staff_check(user):
    return user.is_staff

@login_required
def inventory_dashboard(request):
    """View for inventory dashboard"""
    summary = InventoryService.get_inventory_summary()
    analytics = InventoryService.get_stock_analytics()
    
    context = {
        'summary': summary,
        'analytics': analytics.get('analytics', []),
        'page_title': 'Inventory Dashboard',
        'refresh_interval': request.GET.get('refresh', 60000),
        'view_type': request.GET.get('view', 'grid'),
        'date_range': request.GET.get('range', '30'),
    }
    
    return render(request, 'inventory_dashboard.html', context)

@login_required
def low_stock_alerts(request):
    """View for low stock alerts"""
    threshold = request.GET.get('threshold', 10)
    try:
        threshold = int(threshold)
    except ValueError:
        threshold = 10
        
    alerts = InventoryService.get_low_stock_alerts(threshold)
    
    context = {
        'threshold': threshold,
        'alerts': alerts,
        'page_title': 'Low Stock Alerts',
        'alert_levels': {
            'critical': request.GET.get('critical', 5),
            'warning': request.GET.get('warning', 10),
            'normal': request.GET.get('normal', 20)
        },
        'sort_by': request.GET.get('sort', 'quantity'),
        'filter_category': request.GET.get('category', ''),
    }
    
    return render(request, 'low_stock_alerts.html', context)

@login_required
@user_passes_test(staff_check)
def product_detail_view(request, slug):
    """View to display product details with inventory information"""
    product = get_object_or_404(Product, slug=slug)
    
    # Get product analytics from service
    analytics_data = InventoryService.get_stock_analytics()
    
    # Find analytics for this specific product
    analytics = None
    if 'analytics' in analytics_data:
        for item in analytics_data.get('analytics', []):
            if item.get('id') == product.id:
                analytics = item
                break
    
    # Get category averages for comparison chart
    category_data = {}
    categories = Product.objects.values_list('category', flat=True).distinct()
    for category in categories:
        avg_stock = Product.objects.filter(category=category).aggregate(Avg('stock_quantity'))
        category_count = Product.objects.filter(category=category).count()
        category_data[category] = {
            'avg_stock': round(avg_stock['stock_quantity__avg'] or 0, 1),
            'count': category_count
        }
    
    # Get chart time period from request
    chart_period = request.GET.get('period', 'months')
    
    # Get stock history from service
    stock_history = InventoryService.get_stock_history(product.id, period=chart_period)
    
    # Generate sales data that correlates with stock changes
    stock_values = stock_history.get('values', [])
    labels = stock_history.get('labels', [])
    
    # Calculate realistic sales data based on stock changes
    sales_data = []
    for i in range(len(stock_values) - 1):
        if i < len(stock_values) - 1:
            # If stock went down, sales went up (approximately)
            stock_diff = stock_values[i] - stock_values[i+1]
            if stock_diff > 0:
                # Sales are roughly equal to stock decrease plus some randomness
                sales = max(0, stock_diff + random.randint(-2, 2))
            else:
                # If stock increased, sales are just low random numbers
                sales = random.randint(1, 5)
            sales_data.append(sales)
        
    # Add one more value for the current period
    sales_data.append(random.randint(1, 10))
    
    # Get chart colors from request or use defaults
    chart_colors = {
        'primary': request.GET.get('primary_color', '#3b82f6'),
        'secondary': request.GET.get('secondary_color', '#6b7280'),
        'success': request.GET.get('success_color', '#10b981'),
        'warning': request.GET.get('warning_color', '#f59e0b'),
        'danger': request.GET.get('danger_color', '#ef4444'),
    }
    
    # Get stock thresholds from request or use defaults
    stock_thresholds = {
        'critical': int(request.GET.get('critical_threshold', 5)),
        'warning': int(request.GET.get('warning_threshold', 10)),
    }
    
    # Get chart settings from request
    chart_settings = {
        'show_points': request.GET.get('show_points', 'true') == 'true',
        'fill_area': request.GET.get('fill_area', 'true') == 'true',
        'tension': float(request.GET.get('tension', 0.3)),
        'refresh_interval': int(request.GET.get('refresh_interval', 60000)),
    }
    
    # Calculate max velocity for gauge chart
    max_velocity = 10
    remaining_velocity = 10
    
    if analytics and 'sales_velocity' in analytics:
        # Find maximum sales velocity in the same category for context
        category_products = Product.objects.filter(category=product.category)
        max_velocity_found = 0
        
        for prod in category_products:
            for item in analytics_data.get('analytics', []):
                if item.get('id') == prod.id and item.get('sales_velocity', 0) > max_velocity_found:
                    max_velocity_found = item.get('sales_velocity')
        
        max_velocity = max(10, round(max_velocity_found * 1.2))  # Set max 20% higher than actual max
        remaining_velocity = max(0, max_velocity - analytics['sales_velocity'])
    
    # Prepare category data for the chart
    category_avg_data = {k: v['avg_stock'] for k, v in category_data.items()}
    category_counts = {k: v['count'] for k, v in category_data.items()}

    skincare_count = Product.objects.filter(category='Skincare').count()
    haircare_count = Product.objects.filter(category='Haircare').count()
    bodycare_count = Product.objects.filter(category='Bodycare').count()

    context = {
        'product': product,
        'analytics': analytics,
        'category_data': json.dumps(category_avg_data),
        'category_counts': json.dumps(category_counts),
        'stock_history': stock_history,
        'sales_data': json.dumps(sales_data),
        'chart_period': chart_period,
        'chart_colors': chart_colors,
        'stock_thresholds': stock_thresholds,
        'chart_settings': chart_settings,
        'remaining_velocity': remaining_velocity,
        'max_velocity': max_velocity,
        'page_title': f"{product.product_name} - Stock Management",
        'skincare_count': skincare_count,
        'haircare_count': haircare_count,
        'bodycare_count': bodycare_count,
    }
    
    return render(request, 'product_detail.html', context)

@login_required
@user_passes_test(staff_check)
def update_stock(request, product_id):
    """View to update product stock quantity"""
    product = get_object_or_404(Product, id=product_id)
    redirect_url = request.GET.get('redirect', 'product_detail')
    
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 0))
            min_quantity = int(request.POST.get('min_quantity', 0))
            
            if quantity < min_quantity:
                messages.error(request, f'Stock quantity cannot be less than {min_quantity}')
                return redirect(redirect_url, slug=product.slug)
            
            result = InventoryService.update_stock_quantity(product_id, quantity)
            
            if 'error' in result:
                messages.error(request, result['error'])
            else:
                # Update Django model to keep it in sync
                product.stock_quantity = quantity
                product.last_updated = timezone.now()
                product.updated_by = request.user.username
                product.save()
                
                success_template = request.POST.get('success_message', 'Stock updated successfully for {product}')
                success_message = success_template.format(product=product.product_name)
                messages.success(request, success_message)
            
            return redirect(redirect_url, slug=product.slug)
        except ValueError:
            messages.error(request, 'Invalid quantity value')
            return redirect(redirect_url, slug=product.slug)
    
    return redirect(redirect_url, slug=product.slug)

@login_required
@user_passes_test(staff_check)
def stock_history_api(request, product_id):
    """API endpoint for stock history data"""
    period = request.GET.get('period', 'months')
    stock_history = InventoryService.get_stock_history(product_id, period=period)
    return JsonResponse(stock_history)

@login_required
@user_passes_test(staff_check)
def category_comparison_api(request):
    """API endpoint for category comparison data"""
    category_data = {}
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    for category in categories:
        avg_stock = Product.objects.filter(category=category).aggregate(Avg('stock_quantity'))
        category_count = Product.objects.filter(category=category).count()
        category_data[category] = {
            'avg_stock': round(avg_stock['stock_quantity__avg'] or 0, 1),
            'count': category_count
        }
    
    chart_data = {k: v['avg_stock'] for k, v in category_data.items()}
    return JsonResponse(chart_data)

@login_required
@user_passes_test(staff_check)
def stock_sales_api(request, product_id):
    """API endpoint for stock vs sales data"""
    period = request.GET.get('period', 'months')
    stock_history = InventoryService.get_stock_history(product_id, period=period)
    
    stock_values = stock_history.get('values', [])
    labels = stock_history.get('labels', [])
    
    sales_data = []
    for i in range(len(stock_values) - 1):
        if i < len(stock_values) - 1:
            stock_diff = stock_values[i] - stock_values[i+1]
            if stock_diff > 0:
                sales = max(0, stock_diff + random.randint(-2, 2))
            else:
                sales = random.randint(1, 5)
            sales_data.append(sales)
    
    sales_data.append(random.randint(1, 10))
    
    return JsonResponse({
        'labels': labels,
        'stock': stock_values,
        'sales': sales_data
    })