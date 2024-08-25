from django.views.generic import ListView, DetailView, FormView, DeleteView
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from products.models import Product
from .models import FinishedOrder, FinishedProduct
from .forms import FinishedOrderForm, FinishedOrderUpdateForm
from django.utils import timezone
from datetime import datetime
from django.utils.timezone import make_aware
import json
import csv
import re

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
    context_object_name = 'finished_order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        finished_products = self.object.finished_products.all()

        finished_data = []
        total_quantity = 0

        for product in finished_products:
            finished_data.append({
                'product': product.product.name,
                'quantity': product.quantity
                # Removido o campo 'date', pois não existe mais em FinishedProduct
            })
            total_quantity += product.quantity

        context['finished_data'] = finished_data
        context['total_quantity'] = total_quantity
        return context

class FinishedOrderCreateView(FormView):
    template_name = 'finished_order_create.html'
    form_class = FinishedOrderForm

    def form_valid(self, form):
        order = FinishedOrder.objects.create(finished_date=timezone.now())

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

def finished_order_upload(request):
    if request.method == 'POST':

        # Verifica se o arquivo foi enviado
        if 'csv_file' not in request.FILES:
            messages.error(request, 'Nenhum arquivo foi enviado.')
            return redirect('finished_order_upload')

        csv_file = request.FILES['csv_file']

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Por favor, envie um arquivo .csv.')
            return redirect('finished_order_upload')

        try:
            file_data = csv_file.read().decode('utf-8').splitlines()

            # Remover BOM da primeira linha se estiver presente
            if file_data[0].startswith('\ufeff'):
                file_data[0] = file_data[0].replace('\ufeff', '')

            csv_reader = csv.reader(file_data, delimiter=';')

            current_order = None

            for row in csv_reader:

                if not any(row):
                    # Linha é delimitador de bloco de FinishedOrder (dois pontos e vírgula)
                    current_order = None
                    continue

                if len(row) == 2 and row[0] and row[1] and row[0].count('-') == 2 and row[1].count(':') == 2:
                    # Linha é a data e hora da FinishedOrder
                    naive_datetime = datetime.strptime(f"{row[0]} {row[1]}", '%Y-%m-%d %H:%M:%S')
                    finished_date = make_aware(naive_datetime)
                    current_order = FinishedOrder.objects.create(finished_date=finished_date)
                elif len(row) == 2 and current_order:
                    # Linha é um FinishedProduct
                    product_id, quantity = row

                    # Verifica se a linha não é vazia
                    if product_id.isdigit() and quantity.isdigit():
                        # Buscar o produto pelo ID
                        try:
                            product = Product.objects.get(id=product_id)
                        except Product.DoesNotExist:
                            messages.error(request, f'Produto com ID {product_id} não encontrado.')
                            continue

                        # Criar o FinishedProduct e associá-lo à FinishedOrder
                        FinishedProduct.objects.create(
                            order=current_order,
                            product=product,
                            quantity=int(quantity)
                        )
                    else:
                        continue

                else:
                    messages.error(request, f'Formato inválido na linha: {";".join(row)}')
                    continue

            messages.success(request, 'Produtos finalizados foram adicionados com sucesso!')
        except Exception as e:
            messages.error(request, f'Houve um erro ao processar o arquivo: {e}')
            return redirect('finished_order_upload')

        return redirect('finished_order_list')

    return render(request, 'finished_order_upload.html')

class FinishedOrderDeleteView(DeleteView):
    model = FinishedOrder
    template_name = 'finished_order_confirm_delete.html'
    success_url = reverse_lazy('finished_order_list')
