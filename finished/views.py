from django.views.generic import ListView, DetailView, FormView, DeleteView
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from core.mixins import CustomPermissionDeniedMixin
from django.urls import reverse, reverse_lazy
from products.models import Product
from .models import FinishedOrder, FinishedProduct
from .forms import FinishedOrderForm, FinishedOrderUpdateForm
from django.utils import timezone
from datetime import datetime
from django.utils.timezone import make_aware
from django.http import HttpResponseRedirect
import json
import csv

class FinishedOrderListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = FinishedOrder
    template_name = 'finished_order_list.html'
    context_object_name = 'orders_with_totals'
    permission_required = 'finished.view_finishedorder'
    raise_exception = True

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

class FinishedOrderDetailView(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    model = FinishedOrder
    template_name = 'finished_order_detail.html'
    context_object_name = 'finished_order'
    permission_required = 'finished.view_finishedorder'
    raise_exception = True

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

class FinishedOrderCreateView(CustomPermissionDeniedMixin, LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = 'finished_order_create.html'
    form_class = FinishedOrderForm
    permission_required = 'finished.add_finishedorder'
    raise_exception = True
    redirect_url = 'dashboard'

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
    
    def handle_no_permission(self):
        messages.warning(self.request, 'Você não tem permissão. Fale com a administração!')
        return redirect('finished_order_list')

@login_required
@permission_required('finished.change_finishedorder', raise_exception=True)
def finished_order_update_view(request, pk):
    order = get_object_or_404(FinishedOrder, pk=pk)
    products = Product.objects.all()
    finished_products = order.finished_products.all()

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

        # Atualize ou crie os FinishedProducts
        for product_id in selected_products:
            quantity = quantities.get(int(product_id), 0)
            finished_product = FinishedProduct.objects.filter(order=order, product_id=product_id).first()
            
            if finished_product:
                # Atualiza o existente
                finished_product.quantity = quantity
                finished_product.save()
            else:
                # Cria um novo se não existir
                FinishedProduct.objects.create(
                    order=order,
                    product_id=product_id,
                    quantity=quantity,
                    finished_date=order.finished_date
                )

        return redirect('finished_order_detail', pk=order.pk)

    product_quantities = {prod.product.id: prod.quantity for prod in finished_products}

    context = {
        'order': order,
        'products': products,
        'product_quantities': json.dumps(product_quantities),
    }

    return render(request, 'finished_order_update.html', context)

@login_required
@permission_required('finished.add_finishedorder', raise_exception=True)
def finished_order_upload(request):
    if request.method == 'POST':
        print("Formulário submetido via POST.")

        # Verifica se o arquivo foi enviado
        if 'csv_file' not in request.FILES:
            print("Nenhum arquivo foi enviado.")
            messages.error(request, 'Nenhum arquivo foi enviado.')
            return redirect('finished_order_upload')

        csv_file = request.FILES['csv_file']
        print(f"Arquivo recebido: {csv_file.name}")

        if not csv_file.name.endswith('.csv'):
            print("O arquivo enviado não é um .csv")
            messages.error(request, 'Por favor, envie um arquivo .csv.')
            return redirect('finished_order_upload')

        try:
            file_data = csv_file.read().decode('utf-8').splitlines()
            print(f"Arquivo lido com sucesso, número de linhas: {len(file_data)}")

            # Remover BOM da primeira linha se estiver presente
            if file_data[0].startswith('\ufeff'):
                file_data[0] = file_data[0].replace('\ufeff', '')
                print("BOM removido da primeira linha.")

            csv_reader = csv.reader(file_data, delimiter=';')

            current_order = None
            finished_date = None

            for row in csv_reader:
                print(f"Processando linha: {row}")

                # Ignorar linhas vazias
                if not any(row):
                    print("Encontrado delimitador de bloco ou linha vazia, finalizando o bloco atual.")
                    current_order = None
                    finished_date = None
                    continue

                # Verificar se a linha é de FinishedOrder (data e hora)
                if len(row) == 2 and row[0].count('-') == 2 and row[1].count(':') == 2:
                    print(f"Tentando processar a data e hora: {row[0]} {row[1]}")
                    try:
                        finished_datetime = make_aware(datetime.strptime(f"{row[0]} {row[1]}", '%Y-%m-%d %H:%M:%S'))
                        finished_date = finished_datetime.date()  # Extrai apenas a data
                        current_order = FinishedOrder.objects.create(finished_date=finished_datetime)
                        print(f"FinishedOrder criado com data: {finished_date}")
                    except ValueError as e:
                        print(f"Erro ao processar a data e hora '{row[0]} {row[1]}': {e}")
                        messages.error(request, f"Erro ao processar a data e hora '{row[0]} {row[1]}': {e}")
                        return redirect('finished_order_upload')
                
                # Verificar se a linha é de FinishedProduct
                elif len(row) >= 2 and current_order:
                    product_id, quantity = row[0], row[1]

                    # Se o FinishedProduct não tiver uma data, use a data da FinishedOrder
                    if len(row) == 3 and row[2]:
                        product_date = row[2]
                    else:
                        product_date = finished_date

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

                        FinishedProduct.objects.create(
                            order=current_order,
                            product=product,
                            quantity=int(quantity),
                            finished_date=product_date
                        )
                        print(f"FinishedProduct criado: {product.name}, quantidade: {quantity}, data: {product_date}")
                    else:
                        print(f"Produto ID {product_id} ignorado devido à quantidade inválida ou em branco.")
                        continue

                else:
                    print(f"Formato inválido na linha: {row}")
                    messages.error(request, f'Formato inválido na linha: {";".join(row)}')
                    continue

            messages.success(request, 'Produtos finalizados foram adicionados com sucesso!')
            print("Produtos finalizados foram adicionados com sucesso!")
        except Exception as e:
            print(f"Erro ao processar o arquivo: {e}")
            messages.error(request, f'Houve um erro ao processar o arquivo: {e}')
            return redirect('finished_order_upload')

        return redirect('finished_order_list')

    print("GET request - renderizando o template de upload.")
    return render(request, 'finished_order_upload.html')

class FinishedOrderDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = FinishedOrder
    template_name = 'finished_order_confirm_delete.html'
    success_url = reverse_lazy('finished_order_list')
    permission_required = 'finished.delete_finishedorder'
    raise_exception = True

    def form_valid(self, form):
        # Obter o FinishedOrder que será deletado
        finished_order = self.get_object()

        # Iterar sobre todos os FinishedProduct associados e deletar cada um
        for finished_product in finished_order.finished_products.all():
            finished_product.delete()  # Chama o delete customizado que ajusta o estoque

        # Agora, deletar a FinishedOrder
        finished_order.delete()

        # Redirecionar após a exclusão
        return HttpResponseRedirect(self.success_url)
