from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django import forms
from django.db import models
from django.http import JsonResponse
import json
from .models import Product, Category, Review, Order, OrderItem

# Получаем модель пользователя
User = get_user_model()

# КАСТОМНЫЕ ФОРМЫ ДЛЯ CustomUser
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True)
    
    class Meta:
        model = User  # Используем CustomUser, полученный через get_user_model()
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Имя пользователя',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
        help_texts = {
            'username': 'Обязательно. Не более 150 символов. Только буквы, цифры и @/./+/-/_.',
        }

class RussianAuthForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

# Основные view
def home(request):
    products = Product.objects.filter(is_active=True)[:8]
    return render(request, 'home.html', {'products': products})

from django.db import models  # добавь этот импорт в начало файла

def catalog(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    # ПОИСК (добавь этот блок в самое начало, после фильтров)
    query = request.GET.get('q')
    if query:
        products = products.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(brand__icontains=query)
        )
    
    # Фильтр по категории
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Фильтр по размеру
    size = request.GET.get('size')
    if size:
        products = products.filter(size=size)
    
    # Фильтр по цвету
    color = request.GET.get('color')
    if color:
        products = products.filter(color=color)
    
    # Фильтр по бренду
    brand = request.GET.get('brand')
    if brand:
        products = products.filter(brand=brand)
    
    # Фильтр по цене
    price_min = request.GET.get('price_min')
    if price_min:
        products = products.filter(price__gte=price_min)
    
    price_max = request.GET.get('price_max')
    if price_max:
        products = products.filter(price__lte=price_max)
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'catalog.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    reviews = Review.objects.filter(product=product, is_approved=True).order_by('-created_at')
    
    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment,
                is_approved=False
            )
            messages.success(request, 'Спасибо за отзыв! Он появится после проверки.')
        else:
            messages.error(request, 'Заполните все поля')
        
        return redirect('product_detail', product_id=product_id)
    
    return render(request, 'product.html', {
        'product': product,
        'reviews': reviews
    })


def about(request):
    return render(request, 'about.html')

def contacts(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Проверка на пустые поля
        if name and email and message:
            try:
                # Отправка письма на почту магазина
                full_message = f"От: {name} ({email})\n\nТема: {subject}\n\nСообщение:\n{message}"
                
                send_mail(
                    subject=f"Сообщение от {name} | MoveMasters",
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['support@MoveMasters.ru'],  # Сюда почту магазина
                    fail_silently=False,
                )
                messages.success(request, 'Спасибо! Ваше сообщение отправлено. Мы ответим вам в ближайшее время.')
            except Exception as e:
                messages.error(request, 'Произошла ошибка при отправке. Пожалуйста, попробуйте позже или свяжитесь с нами по телефону.')
        else:
            messages.error(request, 'Пожалуйста, заполните все обязательные поля.')
        
        return redirect('contacts')
    
    return render(request, 'contacts.html')


def cart(request):
    products = Product.objects.all()
    # Создаём словарь {id товара: количество на складе}
    product_stock = {p.id: p.stock_quantity for p in products}
    return render(request, 'cart.html', {'product_stock': product_stock})

def checkout(request):
    if request.method == 'POST':
        # Получаем данные из формы
        print("=== ПОСТУПИЛ ЗАПРОС НА ОФОРМЛЕНИЕ ===")
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        cart_data = request.POST.get('cart_data')  # JSON с товарами из корзины
        
        print(f"Имя: {name}, Телефон: {phone}")  # ← ОТЛАДКА

        if not cart_data:
            messages.error(request, 'Корзина пуста')
            return redirect('cart')
        
        # Разбираем корзину
        cart = json.loads(cart_data)
        
        # Считаем общую сумму
        total = 0
        for item in cart:
            total += float(item['price']) * int(item['quantity'])
        
        # Создаём заказ
        order = Order.objects.create(
            guest_name=name,
            guest_email=email,
            phone=phone,
            address=address,
            total_amount=total,
            status='pending'
        )
        
        # ПРИВЯЗКА К ПОЛЬЗОВАТЕЛЮ (если авторизован)
        if request.user.is_authenticated:
            order.user = request.user
            order.save()
        
        # Создаём позиции заказа
        for item in cart:
            product = Product.objects.get(id=item['id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                unit_price=item['price']
            )
        
        messages.success(request, f'Заказ #{order.id} успешно оформлен!')
        return redirect('home')
    
    return redirect('cart')

# Личный кабинет
@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.phone = request.POST.get('phone', '')      # ← добавить
        user.address = request.POST.get('address', '')  # ← добавить
        user.save()
        messages.success(request, 'Данные успешно обновлены!')
        return redirect('profile')
    
    return render(request, 'profile.html', {
        'orders': orders,
        'user': request.user
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = RussianAuthForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = RussianAuthForm()
    
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Используем кастомную форму
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы')
    return redirect('home')

@login_required
def admin_panel(request):
    if not request.user.is_staff:
        return redirect('home')
    
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()  # Используем User, полученный в начале
    
    return render(request, 'admin.html', {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users
    })

def api_products(request):
    products = Product.objects.filter(is_active=True).values('id', 'name', 'price', 'image')
    return JsonResponse(list(products), safe=False)