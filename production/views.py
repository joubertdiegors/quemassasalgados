from django.views.generic import ListView, DetailView, FormView, DeleteView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from products.models import Product
from .models import Production, ProductionOrder
from .forms import ProductionOrderForm, ProductionOrderUpdateForm
from datetime import date
import json
from django.http import HttpResponseRedirect

class ProductionOrderListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = ProductionOrder
    template_name = 'production_order_list.html'
    context_object_name = 'orders_with_totals'
    permission_required = 'production.view_productionorder'
    raise_exception = True

    def get_queryset(self):
        orders = ProductionOrder.objects.all()
        orders_with_totals = []
        for order in orders:
            total_quantity = sum([production.quantity for production in order.productions.all()])
            orders_with_totals.append({
                'order': order,
                'total_quantity': total_quantity
            })
        return orders_with_totals

class ProductionOrderDetailView(LoginRequiredMixin, DetailView):
    model = ProductionOrder
    template_name = 'production_order_detail.html'
    context_object_name = 'order'
    permission_required = 'production.view_productionorder'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productions = self.object.productions.all()

        production_data = []
        total_quantity = 0

        for production in productions:
            production_data.append({
                'product': production.product.name,
                'quantity': production.quantity,
                'date': production.production_date
            })
            total_quantity += production.quantity

        context['production_data'] = production_data
        context['total_quantity'] = total_quantity
        return context

class ProductionOrderCreateView(LoginRequiredMixin, FormView):
    template_name = 'production_order_create.html'
    form_class = ProductionOrderForm
    permission_required = 'production.add_productionorder'
    raise_exception = True

    def form_valid(self, form):
        order = ProductionOrder.objects.create(order_date=date.today())

        selected_products = form.cleaned_data['products']
        for product in selected_products:
            quantity = form.cleaned_data.get(f'quantity_{product.id}', 0)
            if quantity > 0:
                Production.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    production_date=order.order_date
                )

        return redirect(reverse('production_order_detail', kwargs={'pk': order.pk}))

@permission_required('production.change_productionorder', raise_exception=True)
@login_required
def production_order_update_view(request, pk):
    order = get_object_or_404(ProductionOrder, pk=pk)
    products = Product.objects.all()
    productions = order.productions.all()

    if request.method == 'POST':
        selected_products = request.POST.getlist('products')
        quantities = {}

        for k, v in request.POST.items():
            if k.startswith('quantity_'):
                try:
                    product_id = int(k.split('_')[1])
                    quantity = int(v) if v.isdigit() else 0
                    quantities[product_id] = quantity
                except ValueError:
                    continue

        # Atualize ou crie os Production
        for product_id in selected_products:
            quantity = quantities.get(int(product_id), 0)
            production = Production.objects.filter(order=order, product_id=product_id).first()
            
            if production:
                production.quantity = quantity
                production.save()
            else:
                Production.objects.create(
                    order=order,
                    product_id=product_id,
                    quantity=quantity,
                    production_date=order.order_date
                )

        return redirect('production_order_detail', pk=order.pk)

    product_quantities = {prod.product.id: prod.quantity for prod in productions}

    context = {
        'order': order,
        'products': products,
        'product_quantities': json.dumps(product_quantities),
    }

    return render(request, 'production_order_update.html', context)

class ProductionOrderDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = ProductionOrder
    template_name = 'production_order_confirm_delete.html'
    success_url = reverse_lazy('production_order_list')
    permission_required = 'production.delete_productionorder'
    raise_exception = True

    def form_valid(self, form):
        production_order = self.get_object()

        for production in production_order.productions.all():
            production.delete()

        production_order.delete()

        return HttpResponseRedirect(self.success_url)
