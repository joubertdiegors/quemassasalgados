from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Product
from .forms import ProductForm


class ProductListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    permission_required = 'products.view_product'
    raise_exception = True


class ProductCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'product_create.html'
    form_class = ProductForm
    permission_required = 'products.add_product'
    raise_exception = True

    def form_valid(self, form):
        form.save()
        return redirect('product_list')


class ProductUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'product_create.html'
    form_class = ProductForm
    permission_required = 'products.change_product'
    raise_exception = True

    def form_valid(self, form):
        form.save()
        return redirect('product_list')

