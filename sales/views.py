from django.views.generic import ListView, DetailView, FormView, DeleteView
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from products.models import Product
from .models import SalesOrder, SalesProduct
from .forms import SalesOrderForm, SalesOrderUpdateForm
from django.utils import timezone
from datetime import datetime
from django.utils.timezone import make_aware
from django.http import HttpResponseRedirect
import json
import csv

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
    context_object_name = 'sales_order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sales_products = self.object.sales_products.all()

        sales_data = []
        total_quantity = 0

        for product in sales_products:
            sales_data.append({
                'product': product.product.name,
                'quantity': product.quantity,
                'date': product.sale_date
            })
            total_quantity += product.quantity

        context['sales_data'] = sales_data
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
    sales_products = order.sales_products.all()

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

        # Atualize ou crie os SalesProducts
        for product_id in selected_products:
            quantity = quantities.get(int(product_id), 0)
            sales_product = SalesProduct.objects.filter(order=order, product_id=product_id).first()
            
            if sales_product:
                # Atualiza o existente
                sales_product.quantity = quantity
                sales_product.save()
            else:
                # Cria um novo se não existir
                SalesProduct.objects.create(
                    order=order,
                    product_id=product_id,
                    quantity=quantity,
                    sale_date=order.sale_date
                )

        return redirect('sales_order_detail', pk=order.pk)

    product_quantities = {prod.product.id: prod.quantity for prod in sales_products}

    context = {
        'order': order,
        'products': products,
        'product_quantities': json.dumps(product_quantities),
    }

    return render(request, 'sales_order_update.html', context)

def sales_order_upload(request):
    if request.method == 'POST':
        print("Formulário submetido via POST.")

        # Verifica se o arquivo foi enviado
        if 'csv_file' not in request.FILES:
            print("Nenhum arquivo foi enviado.")
            messages.error(request, 'Nenhum arquivo foi enviado.')
            return redirect('sales_order_upload')

        csv_file = request.FILES['csv_file']
        print(f"Arquivo recebido: {csv_file.name}")

        if not csv_file.name.endswith('.csv'):
            print("O arquivo enviado não é um .csv")
            messages.error(request, 'Por favor, envie um arquivo .csv.')
            return redirect('sales_order_upload')

        try:
            file_data = csv_file.read().decode('utf-8').splitlines()
            print(f"Arquivo lido com sucesso, número de linhas: {len(file_data)}")

            # Remover BOM da primeira linha se estiver presente
            if file_data[0].startswith('\ufeff'):
                file_data[0] = file_data[0].replace('\ufeff', '')
                print("BOM removido da primeira linha.")

            csv_reader = csv.reader(file_data, delimiter=';')

            current_order = None
            sale_date = None

            for row in csv_reader:
                print(f"Processando linha: {row}")

                # Ignorar linhas vazias
                if not any(row):
                    print("Encontrado delimitador de bloco ou linha vazia, finalizando o bloco atual.")
                    current_order = None
                    sale_date = None
                    continue

                # Verificar se a linha é de SalesOrder (data e hora)
                if len(row) == 2 and row[0].count('-') == 2 and row[1].count(':') == 2:
                    print(f"Tentando processar a data e hora: {row[0]} {row[1]}")
                    try:
                        sale_datetime = make_aware(datetime.strptime(f"{row[0]} {row[1]}", '%Y-%m-%d %H:%M:%S'))
                        sale_date = sale_datetime.date()  # Extrai apenas a data
                        current_order = SalesOrder.objects.create(sale_date=sale_datetime)
                        print(f"SalesOrder criado com data: {sale_date}")
                    except ValueError as e:
                        print(f"Erro ao processar a data e hora '{row[0]} {row[1]}': {e}")
                        messages.error(request, f"Erro ao processar a data e hora '{row[0]} {row[1]}': {e}")
                        return redirect('sales_order_upload')
                
                # Verificar se a linha é de SalesProduct
                elif len(row) >= 2 and current_order:
                    product_id, quantity = row[0], row[1]

                    # Se o SalesProduct não tiver uma data, use a data da SalesOrder
                    if len(row) == 3 and row[2]:
                        product_date = row[2]
                    else:
                        product_date = sale_date

                    if quantity.strip() == "":
                        print(f"Quantidade em branco para o produto ID {product_id}, linha ignorada.")
                        continue

                    if product_id.isdigit() and quantity.isdigit():
                        try:
                            product = Product.objects.get(id=product_id)
                            print(f"Produto encontrado: {product.name}")
                        except Product.DoesNotExist:
                            print(f"Produto com ID {product_id} não encontrado.")
                            messages.error(request, f'Produto com ID {product_id} não encontrado.')
                            continue

                        SalesProduct.objects.create(
                            order=current_order,
                            product=product,
                            quantity=int(quantity),
                            sale_date=product_date
                        )
                        print(f"SalesProduct criado: {product.name}, quantidade: {quantity}, data: {product_date}")
                    else:
                        print(f"Produto ID {product_id} ignorado devido à quantidade inválida ou em branco.")
                        continue

                else:
                    print(f"Formato inválido na linha: {row}")
                    messages.error(request, f'Formato inválido na linha: {";".join(row)}')
                    continue

            messages.success(request, 'Produtos vendidos foram adicionados com sucesso!')
            print("Produtos vendidos foram adicionados com sucesso!")
        except Exception as e:
            print(f"Erro ao processar o arquivo: {e}")
            messages.error(request, f'Houve um erro ao processar o arquivo: {e}')
            return redirect('sales_order_upload')

        return redirect('sales_order_list')

    print("GET request - renderizando o template de upload.")
    return render(request, 'sales_order_upload.html')

class SalesOrderDeleteView(DeleteView):
    model = SalesOrder
    template_name = 'sales_order_confirm_delete.html'
    success_url = reverse_lazy('sales_order_list')

    def form_valid(self, form):
        # Obter o SalesOrder que será deletado
        sales_order = self.get_object()

        # Iterar sobre todos os SalesProduct associados e deletar cada um
        for sales_product in sales_order.sales_products.all():
            sales_product.delete()  # Chama o delete customizado que ajusta o estoque

        # Agora, deletar a SalesOrder
        sales_order.delete()

        # Redirecionar após a exclusão
        return HttpResponseRedirect(self.success_url)
