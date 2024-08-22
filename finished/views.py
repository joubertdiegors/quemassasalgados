from django.views.generic import ListView, DetailView, FormView, DeleteView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from products.models import Product
from .models import FinishedOrder, FinishedProduct
from .forms import FinishedOrderForm, FinishedOrderUpdateForm
from datetime import date
import json

class FinishedOrderListView(ListView):
    model = FinishedOrder
    template_name = 'finished_order_list.html'
    context_object_name = 'orders_with_totals'

    def get_queryset(self):
        orders = FinishedOrder.objects.all()
        orders_with_totals = []
        for order in orders:
            total_quantity = sum([product.quantity for product in order.finished_products.all()])
            orders_with_totals.append({
                'order': order,
                'total_quantity': total_quantity
            })
        return orders_with_totals

class FinishedOrderDetailView(DetailView):
    model = FinishedOrder
    template_name = 'finished_order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        finished_products = self.object.finished_products.all()

        finished_data = []
        total_quantity = 0

        for product in finished_products:
            finished_data.append({
                'product': product.product.name,
                'quantity': product.quantity,
                'date': product.finished_date
            })
            total_quantity += product.quantity

        context['finished_data'] = finished_data
        context['total_quantity'] = total_quantity
        return context

class FinishedOrderCreateView(FormView):
    template_name = 'finished_order_create.html'
    form_class = FinishedOrderForm

    def form_valid(self, form):
        order = FinishedOrder.objects.create(finished_date=date.today())

        selected_products = form.cleaned_data['products']
        for product in selected_products:
            quantity = form.cleaned_data.get(f'quantity_{product.id}', 0)
            if quantity > 0:
                FinishedProduct.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    finished_date=order.finished_date
                )

        return redirect(reverse('finished_order_detail', kwargs={'pk': order.pk}))

def finished_order_update_view(request, pk):
    order = get_object_or_404(FinishedOrder, pk=pk)
    products = Product.objects.all()
    finished_products = order.finished_products.all()

    product_quantities = {prod.product.id: prod.quantity for prod in finished_products}

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

        FinishedProduct.objects.filter(order=order).delete()

        for product_id in selected_products:
            quantity = quantities.get(int(product_id), 0)
            if quantity > 0:
                FinishedProduct.objects.create(
                    order=order,
                    product_id=product_id,
                    quantity=quantity,
                    finished_date=order.finished_date
                )

        return redirect('finished_order_detail', pk=order.pk)

    context = {
        'order': order,
        'products': products,
        'product_quantities': json.dumps(product_quantities),
    }

    return render(request, 'finished_order_update.html', context)


class FinishedOrderDeleteView(DeleteView):
    model = FinishedOrder
    template_name = 'finished_order_confirm_delete.html'
    success_url = reverse_lazy('finished_order_list')
