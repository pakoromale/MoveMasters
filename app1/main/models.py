from django.db import models
from django.contrib.auth.models import AbstractUser

# Кастомная модель пользователя
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Покупатель'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField("Роль", max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField("Телефон", max_length=20, blank=True)
    address = models.TextField("Адрес", blank=True)
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("URL", max_length=100, unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name="Родительская категория", null=True, blank=True)
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    image = models.ImageField("Изображение", upload_to='products/', blank=True)
    stock_quantity = models.IntegerField("Количество на складе", default=0)
    material = models.CharField("Материал", max_length=100, blank=True)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
    
    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)  # для гостей
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("Количество", default=1)
    
    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"
    
    def get_total_price(self):
        return self.product.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    guest_email = models.EmailField("Email гостя", blank=True)
    guest_name = models.CharField("Имя гостя", max_length=100, blank=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField("Общая сумма", max_digits=10, decimal_places=2)
    address = models.TextField("Адрес доставки")
    phone = models.CharField("Телефон", max_length=20)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.get_status_display()}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("Количество")
    unit_price = models.DecimalField("Цена за единицу", max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField("Оценка", default=5)  # 1-5
    comment = models.TextField("Комментарий")
    is_approved = models.BooleanField("Одобрен", default=False)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
    
    def __str__(self):
        return f"Отзыв от {self.user} на {self.product}"

    
    def __str__(self):
        return self.title