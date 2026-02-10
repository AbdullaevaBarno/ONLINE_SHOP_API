from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions, filters, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from .filters import ProductFilter, ReviewFilter, CategoryFilter

from .models import *
from .serializers import *

class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = CategoryFilter
    search_fields = ['name', 'slug']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('category')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).prefetch_related('items__product')
    
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """Paydalanıwshınıń sebetin kórsetiw"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @extend_schema(request=CartAddSerializer, responses=CartSerializer)
    @action(detail=False, methods=['post'])
    def add(self, request):
        """Sebetke zat qosıw"""
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)

        if product.stock < quantity:
            return Response({"error": "Qoymada jetkiliksiz"}, status=400)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        item.quantity = quantity if created else item.quantity + quantity
        item.save()
        return Response({"success": "Ónim sebetke qosıldı"}, status=201)

class CartItemViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch', 'delete'] # klient tek óshiriwi yamasa sanın ózgertiwi múmkin

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('order_items__product')

    @extend_schema(request=CheckoutSerializer, responses=OrderSerializer)
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        address = serializer.validated_data['address']
        cart_item_ids = serializer.validated_data.get('cart_item_ids') 
        
        cart = get_object_or_404(Cart, user=user)

        with transaction.atomic():
            # SQL hám Filterlew
            if cart_item_ids:
                cart_items = cart.items.select_related('product').select_for_update(of=('product',)).filter(id__in=cart_item_ids)
            else:
                cart_items = cart.items.select_related('product').select_for_update(of=('product',)).all()

            if not cart_items.exists():
                return Response({"error": "Satıp alıw ushın tovar saylanbaǵan"},
                                status=status.HTTP_400_BAD_REQUEST)

            # Order jaratıw, responseda kóriniwi ushın aldın jaratamız
            order = Order.objects.create(
                user=user, 
                total_price=sum(item.get_total_price() for item in cart_items), 
                address=address, 
                status="kutilmekte"
            )

            order_items_to_create = []
            for item in cart_items:
                if item.product.stock < item.quantity:
                    raise Exception(f"{item.product.name} jetkiliksiz")
                
                item.product.stock -= item.quantity
                item.product.save()

                order_items_to_create.append(OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.get_active_price()
                ))

            OrderItem.objects.bulk_create(order_items_to_create)
            cart_items.delete() # Sebet tazalandı

        return Response({"success": "Buyırtpa rásmiylestirildi",
                          "order": OrderSerializer(order).data },
                            status=status.HTTP_201_CREATED)
        
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_class = ReviewFilter
    http_method_names = ['get', 'post', 'patch', 'delete'] 

    def perform_create(self, serializer):
        user = self.request.user
        product_id = self.request.data.get("product")
        product = get_object_or_404(Product, id=product_id)

        satip_alingan = OrderItem.objects.filter(
        order__user=user, 
        product=product, 
        order__status__in=["tolendi", "jiberildi"] 
    ).exists()

        if not satip_alingan:
            raise ValidationError("Siz bul ónimdi satıp alǵanıńızdan keyin ǵana pikir qaldıra alasız!")

        serializer.save(user=user, product=product) 
