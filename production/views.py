from django.views.generic import ListView, DetailView, FormView, UpdateView, DeleteView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from products.models import Product
from .models import Production, ProductionOrder
from .forms import ProductionOrderForm, ProductionOrderUpdateForm
from datetime import date
import json

class ProductionOrderListView(ListView):
    model = ProductionOrder
    template_name = 'production_order_list.html'
    context_object_name = 'orders_with_totals'

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

class ProductionOrderDetailView(DetailView):
    model = ProductionOrder
    template_name = 'production_order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productions = self.object.productions.all()  # Obtém todas as produções relacionadas a esta ordem

        # Prepara os dados para o template
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

class ProductionOrderCreateView(FormView):
    template_name = 'production_order_create.html'
    form_class = ProductionOrderForm

    def form_valid(self, form):
        # Criar uma nova ordem de produção
        order = ProductionOrder.objects.create(order_date=date.today())

        # Captura os produtos selecionados e suas quantidades
        selected_products = form.cleaned_data['products']
        for product in selected_products:
            quantity = form.cleaned_data.get(f'quantity_{product.id}', 0)
            if quantity > 0:
                # Cria uma produção associada à ordem de produção
                Production.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    production_date=order.order_date
                )

        # Redireciona para a página de detalhes da ordem de produção recém-criada
        return redirect(reverse('production_order_detail', kwargs={'pk': order.pk}))

def production_order_update_view(request, pk):
    order = get_object_or_404(ProductionOrder, pk=pk)
    products = Product.objects.all()
    productions = order.productions.all()

    product_quantities = {prod.product.id: prod.quantity for prod in productions}

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

        Production.objects.filter(order=order).delete()

        for product_id in selected_products:
            quantity = quantities.get(int(product_id), 0)
            if quantity > 0:
                Production.objects.create(
                    order=order,
                    product_id=product_id,
                    quantity=quantity,
                    production_date=order.order_date
                )

        return redirect('production_order_detail', pk=order.pk)

    context = {
        'order': order,
        'products': products,
        'product_quantities': json.dumps(product_quantities),  # Passando o dicionário como JSON
    }

    return render(request, 'production_order_update.html', context)


class ProductionOrderDeleteView(DeleteView):
    model = ProductionOrder
    template_name = 'production_order_confirm_delete.html'
    success_url = reverse_lazy('production_order_list')  # Redireciona para a lista de ordens após a exclusão
