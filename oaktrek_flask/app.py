# flask_inventory_api/app.py
import os
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import datetime

# Initialize Django ORM
import settings
from Store.models import Product, Order, OrderItem

app = Flask(__name__)
api = Api(app)

class StockAnalytics(Resource):
    def get(self):
        """Get stock analytics for all products"""
        try:
            products = Product.objects.all()
            analytics = []
            
            for product in products:
                # Calculate sales velocity (items sold per day over last 30 days)
                thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
                
                # Get all order items for this product in the last 30 days
                order_items = OrderItem.objects.filter(
                    product=product,
                    order_order_date_gte=thirty_days_ago
                )
                
                total_sold = sum(item.quantity for item in order_items)
                sales_velocity = total_sold / 30  # Average daily sales
                
                # Assuming you add a stock_quantity field to your Product model
                stock_quantity = getattr(product, 'stock_quantity', 0)
                
                # Calculate days of inventory remaining
                days_remaining = float('inf') if sales_velocity == 0 else stock_quantity / sales_velocity
                
                # Determine stock status
                if days_remaining < 7:
                    stock_status = "Critical"
                elif days_remaining < 14:
                    stock_status = "Low"
                elif days_remaining < 30:
                    stock_status = "Moderate"
                else:
                    stock_status = "Good"
                
                analytics.append({
                    'id': product.id,
                    'name': product.product_name,
                    'category': product.category,
                    'current_stock': stock_quantity,
                    'sales_velocity': round(sales_velocity, 2),
                    'days_remaining': round(days_remaining, 1) if days_remaining != float('inf') else "∞",
                    'stock_status': stock_status
                })
            
            return jsonify({'analytics': analytics})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

class LowStockAlerts(Resource):
    def get(self):
        """Get products with low stock levels"""
        try:
            threshold = int(request.args.get('threshold', 10))
            
            # Assuming you add a stock_quantity field to your Product model
            low_stock_products = []
            for product in Product.objects.all():
                stock_quantity = getattr(product, 'stock_quantity', 0)
                if stock_quantity <= threshold:
                    low_stock_products.append({
                        'id': product.id,
                        'name': product.product_name,
                        'category': product.category,
                        'current_stock': stock_quantity,
                        'price': float(product.price)
                    })
            
            return jsonify({
                'threshold': threshold,
                'count': len(low_stock_products),
                'products': low_stock_products
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

class InventorySummary(Resource):
    def get(self):
        """Get inventory summary by category"""
        try:
            summary = {}
            
            # Get all unique categories
            categories = set(Product.objects.values_list('category', flat=True))
            
            for category in categories:
                products = Product.objects.filter(category=category)
                
                # Assuming you add a stock_quantity field to your Product model
                total_items = sum(getattr(p, 'stock_quantity', 0) for p in products)
                total_value = sum(getattr(p, 'stock_quantity', 0) * p.price for p in products)
                
                summary[category] = {
                    'product_count': products.count(),
                    'total_items': total_items,
                    'total_value': round(total_value, 2)
                }
            
            # Add overall summary
            all_products = Product.objects.all()
            total_items = sum(getattr(p, 'stock_quantity', 0) for p in all_products)
            total_value = sum(getattr(p, 'stock_quantity', 0) * p.price for p in all_products)
            
            return jsonify({
                'categories': summary,
                'overall': {
                    'product_count': all_products.count(),
                    'total_items': total_items,
                    'total_value': round(total_value, 2)
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

class UpdateStock(Resource):
    def put(self, product_id):
        """Update stock quantity for a product"""
        try:
            data = request.get_json()
            product = Product.objects.get(id=product_id)
            
            if 'stock_quantity' in data:
                # Assuming you add a stock_quantity field to your Product model
                product.stock_quantity = data['stock_quantity']
                product.save()
                
            return jsonify({
                'id': product.id,
                'name': product.product_name,
                'current_stock': product.stock_quantity,
                'message': 'Stock updated successfully'
            })
        except Product.DoesNotExist:
            return jsonify({'error': 'Product not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Register API endpoints
api.add_resource(StockAnalytics, '/api/inventory/analytics')
api.add_resource(LowStockAlerts, '/api/inventory/low-stock')
api.add_resource(InventorySummary, '/api/inventory/summary')
api.add_resource(UpdateStock, '/api/inventory/stock/<int:product_id>')
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)