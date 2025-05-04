import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import LuxuryShoe, Bid

# In-memory store for auction state
AUCTION_STATE = {}

class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.luxury_shoe_id = self.scope['url_route']['kwargs']['luxury_shoe_id']
        self.room_group_name = f'auction_{self.luxury_shoe_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Initialize auction state if not exists
        luxury_shoe = await self.get_luxury_shoe()
        
        if self.luxury_shoe_id not in AUCTION_STATE:
            AUCTION_STATE[self.luxury_shoe_id] = {
                'winner': None,
                'end_time': luxury_shoe.auction_end
            }
            
        if luxury_shoe.is_active:
            now = timezone.now()
            if now >= luxury_shoe.auction_start:
                # Use auction_end directly
                expected_end = luxury_shoe.auction_end
                AUCTION_STATE[self.luxury_shoe_id]['end_time'] = expected_end
                
                # Check if auction has already ended
                if now >= expected_end:
                    await self.end_auction(luxury_shoe)
                    highest_bid = await self.get_highest_bid()
                    winner = highest_bid.user.username if highest_bid else None
                    amount = float(highest_bid.amount) if highest_bid else None
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'auction_winner',
                            'winner': winner,
                            'amount': amount
                        }
                    )
                else:
                    # Send auction details
                    await self.send(text_data=json.dumps({
                        'auction_details': {
                            'end_time': expected_end.isoformat(),
                            'is_active': luxury_shoe.is_active,
                            'current_time': now.isoformat()
                        }
                    }))
                    # Start background task to check auction end
                    asyncio.create_task(self.check_auction_end())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def bid_update(self, event):
        await self.send(text_data=json.dumps({
            'bid': event['bid']
        }))

    async def auction_winner(self, event):
        await self.send(text_data=json.dumps({
            'winner': event['winner'],
            'amount': event['amount']
        }))

    async def check_auction_end(self):
        state = AUCTION_STATE[self.luxury_shoe_id]
        luxury_shoe = await self.get_luxury_shoe()
        
        while luxury_shoe.is_active:
            now = timezone.now()
            expected_end = state.get('end_time')
            
            if expected_end and now >= expected_end:
                await self.end_auction(luxury_shoe)
                highest_bid = await self.get_highest_bid()
                winner = highest_bid.user.username if highest_bid else None
                amount = float(highest_bid.amount) if highest_bid else None
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'auction_winner',
                        'winner': winner,
                        'amount': amount
                    }
                )
                break
            
            await asyncio.sleep(1)

    @database_sync_to_async
    def get_highest_bid(self):
        return Bid.objects.filter(luxury_shoe_id=self.luxury_shoe_id).order_by('-amount').first()
        
    @database_sync_to_async
    def get_luxury_shoe(self):
        return LuxuryShoe.objects.get(id=self.luxury_shoe_id)
        
    @database_sync_to_async
    def end_auction(self, shoe):
        if shoe.is_active:
            shoe.is_active = False
            shoe.auction_end = timezone.now()
            shoe.save()