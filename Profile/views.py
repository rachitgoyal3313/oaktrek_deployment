from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import User, Address  # Import custom User model
from Store.models import Order, Product
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import send_mail

import random
import string

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    """Send OTP to user's email"""
    subject = 'Password Reset OTP'
    message = f'Your OTP for password reset is: {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def send_welcome_email(user):
    subject = 'Welcome to OakTrek!'
    from_email = settings.EMAIL_HOST_USER
    to = [user.email]
    
    # Context data for the template
    context = {
        'user': user
    }
    
    # Render HTML content
    html_content = render_to_string('emails/welcome_email.html', context)
    
    # Create plain text version for email clients that don't support HTML
    text_content = strip_tags(html_content)
    
    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, to)
    email.attach_alternative(html_content, "text/html")
    email.send()


def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        cpassword = request.POST.get('password2')
        phone_number = request.POST.get('phone_number')  # Optional phone number field

        if password != cpassword:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(username=name).exists():
            messages.error(request, 'Username already exists')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
        else:
            try:
                user = User.objects.create_user(
                    username=name,
                    email=email,
                    password=password,
                    phone_number=phone_number if phone_number else None
                )
                send_welcome_email(user)
                messages.success(request, 'Registration successful! Please log in.')
                return redirect('auth')
            except IntegrityError as e:
                messages.error(request, f'Error creating user: {str(e)}')
    return render(request, 'auth.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email and password are required')
            return redirect('login')
        
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in successfully!')  # Fixed message
                return redirect('profile')
            else:
                messages.error(request, 'Invalid email or password')
                return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return redirect('login')
    
    return render(request, 'auth.html')

def auth_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    return render(request, 'auth.html')

def logout_view(request):
    logout(request)
    request.session.flush()
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

@login_required
def admin_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email and password are required')
            return redirect('admin_login')
        
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None and user.is_superuser:
                login(request, user)
                messages.success(request, 'Admin login successful!')
                return redirect('admin:index')
            else:
                messages.error(request, 'Invalid credentials or not an admin')
                return redirect('admin_login')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return redirect('admin_login')
    
    return render(request, 'admin_login.html')

@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user)
    addresses = Address.objects.filter(user=request.user)
    is_admin = request.user.is_staff or request.user.is_superuser
    
    return render(request, 'profile.html', {
        'user': request.user,
        'orders': orders,
        'addresses': addresses,
        'is_admin': is_admin,
        'password_changed_at': request.user.password_changed_at
    })

@login_required
def add_address(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        is_default = request.POST.get('is_default') == 'on'

        if not all([name, street, city, state, zipcode]):
            return JsonResponse({
                'status': 'error',
                'message': 'All address fields are required'
            }, status=400)

        try:
            if is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

            address = Address.objects.create(
                name=name, 
                street=street, 
                city=city, 
                state=state,
                zipcode=zipcode, 
                is_default=is_default, 
                user=request.user
            )
            return JsonResponse({
                'status': 'success',
                'message': 'Address added successfully!',
                'address_id': address.id
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    try:
        address.delete()
        messages.success(request, 'Address deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting address: {str(e)}')
    return redirect('profile')

def change_password(request):
    # Check if the request is coming from forgot password or profile
    source = request.GET.get('source', 'profile')
    
    # If user is not authenticated and not coming from forgot password, redirect
    if not request.user.is_authenticated and source != 'forgot':
        messages.error(request, 'Please login to change your password.')
        return redirect('login')
    
    # For forgot password flow, we need to first ask for the email
    if source == 'forgot' and request.method == 'GET' and 'reset_email' not in request.session:
        return render(request, 'change_password.html', {
            'step': 'request_email',
            'source': source
        })
    
    # Process email submission for forgot password
    if source == 'forgot' and 'submit_email' in request.POST:
        email = request.POST.get('email')
        # Verify email exists in the system
        try:
            User.objects.get(email=email)
            request.session['reset_email'] = email
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            return render(request, 'change_password.html', {
                'step': 'request_email',
                'source': source
            })
    
    # Get email from session if coming from forgot password, otherwise use logged in user's email
    email = request.session.get('reset_email', request.user.email if request.user.is_authenticated else None)
    
    if not email:
        messages.error(request, 'Email not found. Please try again.')
        return redirect('login')
    
    # Step 1: Send OTP
    if (request.method == 'GET' and 'reset_email' in request.session) or 'send_otp' in request.POST:
        # Generate OTP and save to session
        otp = generate_otp()
        request.session['password_reset_otp'] = otp
        request.session['reset_email'] = email
        
        # Send OTP to user's email
        send_otp_email(email, otp)
        
        return render(request, 'change_password.html', {
            'step': 'verify_otp',
            'email': email,
            'source': source
        })
    
    # Rest of your function remains the same...
    # Step 2: Verify OTP
    elif 'verify_otp' in request.POST:
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('password_reset_otp')
        
        if entered_otp == stored_otp:
            return render(request, 'change_password.html', {
                'step': 'change_password',
                'email': email,
                'source': source
            })
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, 'change_password.html', {
                'step': 'verify_otp',
                'email': email,
                'source': source
            })
    
    # Step 3: Change Password
    elif 'change_password' in request.POST:
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'change_password.html', {
                'step': 'change_password',
                'email': email,
                'source': source
            })
        
        try:
            # Get user by email
            user = User.objects.get(email=email)
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Update session if user is logged in
            if request.user.is_authenticated:
                update_session_auth_hash(request, user)
            
            # Clear session data
            if 'password_reset_otp' in request.session:
                del request.session['password_reset_otp']
            if 'reset_email' in request.session:
                del request.session['reset_email']
            
            messages.success(request, 'Password changed successfully.')
            
            # Render success page
            return render(request, 'change_password.html', {
                'step': 'success',
                'source': source
            })
            
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('login')
    
    # Default case
    return render(request, 'change_password.html', {
        'step': 'verify_otp',
        'email': email,
        'source': source
    })



@login_required
def add_phone(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone')
        if not phone_number:
            messages.error(request, 'Phone number is required')
            return redirect('profile')

        try:
            request.user.phone_number = phone_number
            request.user.save()
            messages.success(request, 'Phone number updated successfully!')
            return redirect('profile')
        except Exception as e:
            messages.error(request, f'Error updating phone number: {str(e)}')
            return redirect('profile')

@login_required
def admin_signin(request):
    if request.method == 'POST':
        email = request.POST.get('admin_email')
        password = request.POST.get('admin_password')
        
        if not email or not password:
            return JsonResponse({
                'status': 'error',
                'message': 'Email and password are required'
            }, status=400)
        
        try:
            user = User.objects.get(email=email)
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user and authenticated_user.is_superuser:
                login(request, authenticated_user)
                request.session['is_admin'] = True
                return JsonResponse({
                    'status': 'success',
                    'message': 'Admin sign-in successful!',
                    'redirect': reverse('adminProducts')
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid credentials or not a superuser'
                }, status=400)
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'User does not exist'
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)


@login_required
def address_list_view(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'addresses.html', {'addresses': addresses})

@login_required
def update_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number', None)

        if not username or not email:
            return JsonResponse({
                'status': 'error',
                'message': 'Username and email are required'
            }, status=400)

        try:
            user = request.user
            
            # Check if username is already taken by another user
            if User.objects.exclude(pk=user.pk).filter(username=username).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Username already exists'
                }, status=400)
            
            # Check if email is already taken by another user
            if User.objects.exclude(pk=user.pk).filter(email=email).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email already exists'
                }, status=400)

            # Update user fields
            user.username = username
            user.email = email
            if phone_number is not None:
                user.phone_number = phone_number
            user.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Profile updated successfully!'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)


@login_required
def delete_profile(request):
    if request.method == 'POST':
        try:
            # Delete the user
            request.user.delete()
            # Logout the user
            logout(request)
            return JsonResponse({
                'status': 'success',
                'message': 'Your profile has been deleted successfully.'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error deleting profile: {str(e)}'
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@login_required
def admin_products_view(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page')
        return redirect('profile')
    
    from Store.models import Product
    products = Product.objects.all()
    
    return render(request, 'adminProducts.html', {
        'products': products,
        'admin_emails': ['admin@example.com']  # Add your admin emails here
    })

    
@login_required
def add_product(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page')
        return redirect('profile')
    
    if request.method == 'POST':
        try:
            # Extract product data from the form
            product_name = request.POST.get('product_name')
            category = request.POST.get('category')
            gender = request.POST.get('gender')
            price = request.POST.get('price')
            description = request.POST.get('description')
            image_1 = request.FILES.get('image_1')
            
            # Create the product
            product = Product.objects.create(
                product_name=product_name,
                category=category,
                gender=gender,
                price=price,
                description=description,
                image_1=image_1
            )
            
            messages.success(request, 'Product added successfully!')
            return redirect('adminProducts')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
            return redirect('add_product')
    
    # For GET request, render the add product form
    return render(request, 'add_product.html', {
        'categories': Product.CATEGORY_CHOICES,
        'gender_choices': Product.GENDER_CHOICES
    })


@login_required
def view_product(request, product_id):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page')
        return redirect('profile')
    
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'view_product.html', {'product': product})

@login_required
def edit_product(request, product_id):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page')
        return redirect('profile')
    
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        try:
            product.product_name = request.POST.get('product_name')
            product.category = request.POST.get('category')
            product.gender = request.POST.get('gender')
            product.price = request.POST.get('price')
            product.description = request.POST.get('description')
            if request.FILES.get('image_1'):
                product.image_1 = request.FILES.get('image_1')
            product.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('adminProducts')
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    return render(request, 'add_product.html', {
        'product': product,
        'categories': Product.CATEGORY_CHOICES,
        'gender_choices': Product.GENDER_CHOICES,
        'is_edit': True  # Flag to indicate editing mode
    })


@login_required
def delete_product(request, product_id):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page')
        return redirect('profile')
    
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, 'Product deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
        return redirect('adminProducts')
    
    return redirect('adminProducts')

@login_required
def bulk_delete_products(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page')
        return redirect('profile')
    
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        try:
            Product.objects.filter(id__in=product_ids).delete()
            messages.success(request, 'Selected products deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting products: {str(e)}')
        return redirect('adminProducts')
    
    return redirect('adminProducts')

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})
