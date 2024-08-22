from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import redirect
from .models import Product
from .forms import ProductForm

class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'

class ProductCreateView(CreateView):
    model = Product
    template_name = 'product_create.html'
    form_class = ProductForm

    def form_valid(self, form):
        form.save()
        return redirect('product_list')

class ProductUpdateView(UpdateView):
    model = Product
    template_name = 'product_create.html'
    form_class = ProductForm

    def form_valid(self, form):
        form.save()
        return redirect('product_list')

