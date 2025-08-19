from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO

from .models import Product, Cart


# Home Page
def home(request):
    return render(request, 'home.html')


# Signup View
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# Profile View
@login_required
def profile_view(request):
    return render(request, 'profile.html')


# Dashboard View
@login_required

def dashboard_view(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    
    return render(request, 'dashboard.html', {'products': products})



# ✅ Corrected Add to Cart View
@login_required
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')  # Redirects to the cart URL correctly
# This should match the name of your cart page URL


# Cart View

@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


@login_required
def delete_cart_item(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')  # Redirects to the cart URL correctly


# PDF Bill Generation
@login_required
def generate_pdf_bill(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)

    template = get_template('bill.html')
    context = {
        'cart_items': cart_items,
        'total': total,
        'user': request.user
    }

    html = template.render(context)
    response = BytesIO()
    pdf_status = pisa.CreatePDF(html, dest=response)

    if not pdf_status.err:
        return HttpResponse(response.getvalue(), content_type='application/pdf')
    else:
        return HttpResponse("Error generating PDF", status=400)
@login_required
def analytics_view(request):
    from django.db.models import Sum

    # Aggregate product quantities
    cart_items = Cart.objects.filter(user=request.user).values('product__name').annotate(total_quantity=Sum('quantity'))

    product_names = [item['product__name'] for item in cart_items]
    product_quantities = [item['total_quantity'] for item in cart_items]

    context = {
        'product_names': product_names,
        'product_quantities': product_quantities
    }

    return render(request, 'analytics.html', context)

