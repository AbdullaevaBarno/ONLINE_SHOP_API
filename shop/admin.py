from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)} 
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_active', 'category', 'updated_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 
    readonly_fields = ('product', 'price', 'quantity') 

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status',  "address", 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline] 

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')

admin.site.register(Cart)
admin.site.register(CartItem)