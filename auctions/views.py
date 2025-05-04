from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import LuxuryShoe, Bid
from Store.models import Cart
from django.utils import timezone

def auction_list(request):
    auctions = LuxuryShoe.objects.all()
    now = timezone.now()
    
    # Update auction status for all auctions
    for auction in auctions:
        auction.save()  # Triggers save method to update is_active
    
    auction_data = []
    for auction in auctions:
        highest_bid = Bid.objects.filter(luxury_shoe=auction).order_by('-amount').first()
        auction_data.append({
            'auction': auction,
            'highest_bid': highest_bid
        })
    
    return render(request, 'auctions/auction_list.html', {
        'auction_data': auction_data,
        'now': now
    })

@login_required
def auction_detail(request, luxury_shoe_id):
    luxury_shoe = get_object_or_404(LuxuryShoe, id=luxury_shoe_id)
    highest_bid = Bid.objects.filter(luxury_shoe=luxury_shoe).order_by('-amount').first()
    bid_history = Bid.objects.filter(luxury_shoe=luxury_shoe).order_by('-timestamp')
    
    now = timezone.now()
    
    # Update auction status
    luxury_shoe.save()  # Triggers save method to update is_active
    
    if not luxury_shoe.is_active and now >= luxury_shoe.auction_end:
        messages.info(request, 'This auction has ended.')
        if highest_bid:
            if highest_bid.user == request.user:
                messages.success(request, f'You won this auction with a bid of ₹{highest_bid.amount}!')
            else:
                messages.info(request, f'This auction was won by {highest_bid.user.username} with a bid of ₹{highest_bid.amount}.')

    if request.method == 'POST' and luxury_shoe.is_active:
        try:
            bid_amount = float(request.POST.get('amount'))
            if bid_amount <= 0:
                raise ValueError("Bid amount must be positive.")
        except (TypeError, ValueError):
            messages.error(request, 'Please enter a valid bid amount.')
            return render(request, 'auctions/auction_detail.html', {
                'luxury_shoe': luxury_shoe,
                'highest_bid': highest_bid,
                'bids': bid_history,
                'now': now,
                'current_time': timezone.now()
            })

        if highest_bid and bid_amount <= highest_bid.amount:
            messages.error(request, f'Your bid must be higher than ₹{highest_bid.amount}.')
        elif bid_amount < luxury_shoe.starting_bid:
            messages.error(request, f'Your bid must be at least ₹{luxury_shoe.starting_bid}.')
        else:
            with transaction.atomic():
                new_bid = Bid.objects.create(
                    luxury_shoe=luxury_shoe,
                    user=request.user,
                    amount=bid_amount
                )
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'auction_{luxury_shoe_id}',
                    {
                        'type': 'bid_update',
                        'bid': {
                            'user': request.user.username,
                            'amount': bid_amount,
                            'timestamp': new_bid.timestamp.isoformat()
                        }
                    }
                )
            messages.success(request, 'Your bid has been placed successfully!')
            return redirect('auctions:auction_detail', luxury_shoe_id=luxury_shoe_id)

    return render(request, 'auctions/auction_detail.html', {
        'luxury_shoe': luxury_shoe,
        'highest_bid': highest_bid,
        'bids': bid_history,
        'now': now,
        'current_time': timezone.now(),
        'auction_end_time': luxury_shoe.auction_end
    })

def add_product_to_cart(user, product, bid_amount=None):
    cart_item, created = Cart.objects.get_or_create(
        user=user,
        product=product,
        defaults={'quantity': 1, 'bid_amount': bid_amount}
    )
    if not created:
        cart_item.quantity = 1  # Reset to 1 for auction items
        cart_item.bid_amount = bid_amount  # Update bid amount
        cart_item.save()

@login_required
def buy_now(request, luxury_shoe_id):
    luxury_shoe = get_object_or_404(LuxuryShoe, id=luxury_shoe_id)
    highest_bid = Bid.objects.filter(luxury_shoe=luxury_shoe).order_by('-amount').first()
    
    # Update auction status
    luxury_shoe.save()  # Triggers save method to update is_active
    
    if luxury_shoe.is_active:
        messages.error(request, 'This auction is still active.')
        return redirect('auctions:auction_detail', luxury_shoe_id=luxury_shoe_id)
    
    if not highest_bid or highest_bid.user != request.user:
        messages.error(request, 'You are not the winner of this auction.')
        return redirect('auctions:auction_detail', luxury_shoe_id=luxury_shoe_id)
    
    # Clear existing cart items to ensure only the auction item is checked out
    Cart.objects.filter(user=request.user).delete()
    
    # Add the auctioned product to the cart with the bid amount
    add_product_to_cart(request.user, luxury_shoe.product, bid_amount=highest_bid.amount)
    
    # Redirect to checkout
    return redirect('checkout')