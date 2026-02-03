from rest_framework import serializers
from django.utils.text import slugify
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'children']

    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data

class ProductSerializer(serializers.ModelSerializer):
    category_data = CategorySerializer(source='category', read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['slug']

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)

class CartItemSerializer(serializers.ModelSerializer):
    product_data = ProductSerializer(source='product', read_only=True)
    total_price = serializers.ReadOnlyField(source='get_total_price')

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_data', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    grand_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'grand_total']

    def get_grand_total(self, obj):
        return sum(item.get_total_price() for item in obj.items.all())

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'status', 'address', 'created_at', 'order_items']

class CheckoutSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=450, required=True)
    cart_item_ids = serializers.ListField(child=serializers.IntegerField(), required=False)

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = ['id', 'user_name', 'product', 'text', 'rating', 'created_at']