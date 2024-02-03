from django.shortcuts import render, get_object_or_404
from django.http import Http404

from .models import Category, Product


def product_list(request, category_slug=None):
    request.session['salom'] = 'qalesan'
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category,     
                                     slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product/list.html', {'category': category,
                                                      'categories': categories,
                                                      'products': products})
    

def product_detail(request, id, slug):
    try:
        product = Product.objects.filter(id=id, slug=slug, available=True).select_related('category').first()
    except Product.DoesNotExist:
        raise Http404
    return render(request, 'shop/product/detail.html', {'product': product})