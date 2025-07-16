from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from core.mixins import CustomPermissionDeniedMixin
from .models import Product, ProductCategory, Kit, KitOption
from .forms import ProductForm, ProductCategoryForm, KitForm, KitOptionFormSet
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect



@staff_member_required
def category_list(request):
    categories = ProductCategory.objects.all().order_by('name')
    return render(request, 'category_list.html', {'categories': categories})

@staff_member_required
def category_create(request):
    form = ProductCategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'category_form.html', {'form': form, 'title': 'Nova Categoria'})

@staff_member_required
def category_edit(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    form = ProductCategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'category_form.html', {'form': form, 'title': 'Editar Categoria'})

@method_decorator(staff_member_required, name='dispatch')
class CategoryDeleteView(DeleteView):
    model = ProductCategory
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

class ProductListView(CustomPermissionDeniedMixin, PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    permission_required = 'products.view_product'
    raise_exception = True

class ProductCreateView(CustomPermissionDeniedMixin, PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'product_create.html'
    form_class = ProductForm
    permission_required = 'products.add_product'
    raise_exception = True

    def form_valid(self, form):
        form.save()
        return redirect('product_list')

class ProductUpdateView(CustomPermissionDeniedMixin, PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'product_create.html'
    form_class = ProductForm
    permission_required = 'products.change_product'
    raise_exception = True

    def form_valid(self, form):
        form.save()
        return redirect('product_list')

class KitListView(CustomPermissionDeniedMixin, PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Kit
    template_name = 'kit_list.html'
    context_object_name = 'kits'
    permission_required = 'products.view_kit'
    raise_exception = True

class KitCreateView(CustomPermissionDeniedMixin, PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Kit
    form_class = KitForm
    template_name = 'kit_form.html'
    permission_required = 'products.add_kit'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['option_formset'] = KitOptionFormSet(self.request.POST or None)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['option_formset']
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect('kit_list')
        return self.form_invalid(form)
    
class KitUpdateView(CustomPermissionDeniedMixin, PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Kit
    form_class = KitForm
    template_name = 'kit_form.html'
    permission_required = 'products.change_kit'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['option_formset'] = KitOptionFormSet(
            self.request.POST or None,
            instance=self.object
        )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['option_formset']
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.save()
            return redirect('kit_list')
        return self.form_invalid(form)

@user_passes_test(lambda u: u.is_staff)
def duplicate_kit(request, pk):
    original = get_object_or_404(Kit, pk=pk)
    new_kit = Kit.objects.create(
        name=f"{original.name} (Cópia)",
        description=original.description,
        is_active=original.is_active,
        show_on_website=original.show_on_website,
        # Imagem não copiada
    )

    for option in original.options.all():
        KitOption.objects.create(
            kit=new_kit,
            category=option.category,
            max_choices=option.max_choices,
        )

    messages.success(request, f'Kit "{original.name}" duplicado com sucesso.')
    return HttpResponseRedirect(reverse('kit_update', kwargs={'pk': new_kit.pk}))