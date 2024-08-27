from django.views.generic import ListView, DetailView, FormView, DeleteView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from products.models import Product
from .models import SalesOrder, SalesProduct
from .forms import SalesOrderForm, SalesOrderUpdateForm
from django.utils import timezone
from django.http import HttpResponseRedirect
import json

class SalesOrderListView(ListView):
    model = SalesOrder
    template_name = 'sales_order_list.html'
    context_object_name = 'orders_with_totals'

    def get_queryset(self):
        orders = SalesOrder.objects.all()
        orders_with_totals = []
        for order in orders:
            total_quantity = sum([product.quantity for product in order.sales_products.all()])
            orders_with_totals.append({
                'order': order,
                'total_quantity': total_quantity
            })
        return orders_with_totals

class SalesOrderDetailView(DetailView):
    model = SalesOrder
    template_name = 'sales_order_detail.html'
    context_object_name = 'sale_order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sold_products = self.object.sold_products.all()

        sale_data = []
        total_quantity = 0

        for product in sold_products:
            sale_data.append({
                'product': product.product.name,
                'quantity': product.quantity,
                'date': product.sale_date
            })
            total_quantity += product.quantity

        context['sale_data'] = sale_data
        context['total_quantity'] = total_quantity
        return context

class SalesOrderCreateView(FormView):
    template_name = 'sales_order_create.html'
    form_class = SalesOrderForm

    def form_valid(self, form):
        order = SalesOrder.objects.create(sale_date=timezone.now())

        selected_products = form.cleaned_data['products']
        for product in selected_products:
            quantity = form.cleaned_data.get(f'quantity_{product.id}', 0)
            if quantity > 0:
                SalesProduct.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    sale_date=order.sale_date
                )

        return redirect(reverse('sales_order_detail', kwargs={'pk': order.pk}))

def sales_order_update_view(request, pk):
    order = get_object_or_404(SalesOrder, pk=pk)
    products = Product.objects.all()
    sold_products = order.sold_products.all()

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

        # Atualize ou crie os SoldProducts
        for product_id in selected_products:
            quantity = quantities.get(int(product_id), 0)
            sold_product = SalesProduct.objects.filter(order=order, product_id=product_id).first()
            
            if sold_product:
                # Atualiza o existente
                sold_product.quantity = quantity
                sold_product.save()
            else:
                # Cria um novo se não existir
                SalesProduct.objects.create(
                    order=order,
                    product_id=product_id,
                    quantity=quantity,
                    sale_date=order.sale_date
                )

        return redirect('sales_order_detail', pk=order.pk)

    product_quantities = {prod.product.id: prod.quantity for prod in sold_products}

    context = {
        'order': order,
        'products': products,
        'product_quantities': json.dumps(product_quantities),
    }

    return render(request, 'sales_order_update.html', context)

class SalesOrderDeleteView(DeleteView):
    model = SalesOrder
    template_name = 'sales_order_confirm_delete.html'
    success_url = reverse_lazy('sale_order_list')

    def form_valid(self, form):
        # Obter o SaleOrder que será deletado
        sale_order = self.get_object()

        # Iterar sobre todos os SoldProduct associados e deletar cada um
        for sold_product in sale_order.sold_products.all():
            sold_product.delete()  # Chama o delete customizado que ajusta o estoque

        # Agora, deletar a SaleOrder
        sale_order.delete()

        # Redirecionar após a exclusão
        return HttpResponseRedirect(self.success_url)
