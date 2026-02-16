from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from django.utils.text import slugify
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'children']
        
    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_children(self, obj):
        children = obj.children.all()
        
        if children.exists():
            return CategorySerializer(children, many=True).data
        
        return []
    
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
    product = ProductSerializer(read_only=True)
    
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), 
        source="product", 
        write_only=True
    )
    total_price = serializers.ReadOnlyField(source='get_total_price')
    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "total_price"]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()


    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_total_price(self, obj):
        return sum(item.get_total_price() for item in obj.items.all())
    
class CartAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(help_text="Ónimniń ID-si")
    quantity = serializers.IntegerField(default=1, min_value=1, help_text="Neshe dana qosıw kerek? (Minimal 1)")

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity']

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


    extra_kwargs = {
            'rating': {'help_text': '1 den 5 ke shekem baha beriń'}
        }