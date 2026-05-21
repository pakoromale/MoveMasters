// Основные скрипты для сайта (все значения в px)

document.addEventListener('DOMContentLoaded', function() {
    console.log('EcoHome website loaded');
    
    // Анимация при скролле
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.feature-card, .product-card');
        const screenHeight = window.innerHeight;
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const triggerPosition = screenHeight * 0.8; // 80% от высоты экрана
            
            if (elementPosition < triggerPosition) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0px)';
            }
        });
    };
    
    // Изначально скрываем элементы для анимации
    const animatedElements = document.querySelectorAll('.feature-card, .product-card');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    });
    
    // Запускаем анимацию
    setTimeout(animateOnScroll, 100);
    window.addEventListener('scroll', animateOnScroll);
    
    // Кнопки "В корзину"
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            
            // Временный alert
            alert('Товар добавлен в корзину!');
            
            // Можно добавить анимацию
            this.innerHTML = '<i class="bi bi-check"></i> Добавлено';
            this.style.backgroundColor = '#28a745';
            
            setTimeout(() => {
                this.innerHTML = '<i class="bi bi-cart-plus me-2"></i>Добавить в корзину';
                this.style.backgroundColor = '';
            }, 2000);
        });
    });
    
    // Активный пункт меню
    const currentPage = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath === currentPage || 
            (linkPath !== '/' && currentPage.startsWith(linkPath))) {
            link.classList.add('active');
        }
    });
    
    // Простой слайдер (если понадобится)
    const initSlider = () => {
        const slider = document.querySelector('.product-slider');
        if (slider) {
            let currentSlide = 0;
            const slides = slider.querySelectorAll('.slide');
            const totalSlides = slides.length;
            
            if (totalSlides > 1) {
                setInterval(() => {
                    slides[currentSlide].style.display = 'none';
                    currentSlide = (currentSlide + 1) % totalSlides;
                    slides[currentSlide].style.display = 'block';
                }, 5000); // 5 секунд
            }
        }
    };
    
    initSlider();
});