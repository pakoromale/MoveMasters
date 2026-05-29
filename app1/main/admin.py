from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Product, Order, OrderItem, Review 

# Кастомный администратор для пользователей
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff']
    list_filter = ['role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'phone', 'address')}),
    )

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'guest_name', 'user', 'phone', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    search_fields = ('comment', 'user__username')
    list_editable = ('is_approved',)  # можно менять статус прямо из списка

    
# Регистрация моделей
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(OrderItem)
