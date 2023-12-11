from django.shortcuts import render, get_object_or_404

from cart.forms import CartAddProductForm
from .models import Category, Product
from .recommender import Recommender


def product_list(request, catalog_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if catalog_slug:
        language = request.LANGUAGE_CODE
        category = get_object_or_404(Category, translations__language_code=language, translations__slug=catalog_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product/list.html',
                  {'category': category, 'categories': categories, 'products': products})


def product_detail(request, product_id, product_slug):
    language = request.LANGUAGE_CODE
    product = get_object_or_404(Product, id=product_id, translations__language_code=language, translations__slug=product_slug,
                                available=True)
    cart_product_form = CartAddProductForm()
    r = Recommender()
    recommended_products = r.suggest_products_for([product], 4)
    return render(request, 'shop/product/detail.html', {'product': product, 'cart_product_form': cart_product_form,
                                                        'recommended_products': recommended_products})
