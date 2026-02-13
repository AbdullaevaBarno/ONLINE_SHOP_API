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


#Katalog
@extend_schema(tags=['Categories'])
class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = CategoryFilter
    pagination_class = None
    search_fields = ['name', 'slug']

    def get_queryset(self):
        queryset = Category.objects.all().prefetch_related('children')
        
        parent_id = self.request.query_params.get('parent_id')
        search = self.request.query_params.get('search')

        if parent_id or search:
            return queryset
        
        return queryset.filter(parent__isnull=True)

#Ónimler
@extend_schema(tags=['Product'])
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('category')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name']
    ordering_fields = ['price', 'name', 'created_at']
    ordering = ['-created_at']
    http_method_names = ['get']

    class IsAdminOrReadOnly(permissions.BasePermission):

        def has_permission(self, request, view):
            if request.method in permissions.SAFE_METHODS:
                return True
            return request.user and request.user.is_staff

    permission_classes = [IsAdminOrReadOnly]


# Sebet
@extend_schema(tags=['Cart'])
class CartViewSet(GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer
    

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).prefetch_related('items__product')
    
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        #Paydalanıwshı sebetin kórsetiw
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @extend_schema(request=CartAddSerializer, responses=CartSerializer)
    @action(detail=False, methods=['post'])
    def add(self, request):
        #sebetke zat qosıw
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


# Sebet ishindegi elementleri
@extend_schema(tags=['Cart']) 
class CartItemViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete'] # klient tek, kóriwi yaki óshiriwi yamasa sanın ózgertiwi múmkin

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)


# Buyırtpalar
@extend_schema(tags=['Orders & Checkout'])
class OrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
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

            # Order jaratıw
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
            cart_items.delete() 

        return Response({"success": "Buyırtpa rásmiylestirildi",
                          "order": OrderSerializer(order).data },
                            status=status.HTTP_201_CREATED)
    
    @extend_schema(request=None, responses=OrderSerializer)
    @action(detail=True, methods=['post'])
    def t_m(self, request, pk=None):
        order = self.get_object()

        if order.status == 'tólendi':
            return Response(
                {"error": "Bul buyırtpa aldın tólengen. Qayta tólem qılıw múmkin emes."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if order.status == 'biykar_etildi':
            return Response(
                {"error": "Biykar etilgen buyırtpa ushın tólem qabıllanbaydı."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = 'tólendi'
        order.save()

        return Response({
            "message": "Tólem tabıslı pitti!",
            "order_details": OrderSerializer(order).data
        }, status=status.HTTP_200_OK)


# Pikirler
@extend_schema(tags=['Reviews'])
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filterset_class = ReviewFilter
    http_method_names = ['get', 'post', 'patch', 'delete'] 

    class IsOwnerOrReadOnly(permissions.BasePermission):  
        def has_object_permission(self, request, view, obj):
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj.user == request.user

    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        user = self.request.user
        product_id = self.request.data.get("product")
        product = get_object_or_404(Product, id=product_id)

        satip_alingan = OrderItem.objects.filter(
        order__user=user, 
        product=product, 
        order__status__in=["tólendi", "jiberildi"] 
    ).exists()

        if not satip_alingan:
            raise ValidationError("Siz bul ónimdi satıp alǵanıńızdan keyin ǵana pikir qaldıra alasız!")

        serializer.save(user=user, product=product) 
