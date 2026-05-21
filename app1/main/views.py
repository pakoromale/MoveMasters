from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django import forms
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

def catalog(request):
    category_id = request.GET.get('category')
    
    if category_id:
        products = Product.objects.filter(category_id=category_id, is_active=True)
    else:
        products = Product.objects.filter(is_active=True)
    
    categories = Category.objects.all()
    return render(request, 'catalog.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product, is_approved=True)
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
    cart_items = []
    total_price = 0
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

# Оформление заказа (упрощённая версия)
def checkout(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '')
            email = request.POST.get('email', '')
            address = request.POST.get('address', '')
            
            order_number = str(abs(hash(name + email + str(request.user.id if request.user.is_authenticated else ''))))[-6:]
            
            messages.success(request, 
                f'✅ Заказ оформлен! {name}, мы свяжемся с вами по email {email}. ' +
                f'Номер заказа: #{order_number}'
            )
            
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f'Ошибка при оформлении заказа: {str(e)}')
            return redirect('cart')
    
    return redirect('cart')

# Личный кабинет
@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
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