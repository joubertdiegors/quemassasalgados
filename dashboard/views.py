from django.shortcuts import render
from production.models import Production
from finished.models import FinishedProduct
from sales.models import SalesProduct, LeftoverProduct
from collections import defaultdict
from datetime import datetime
import json

from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    # Coletar os dados brutos do banco de dados para FinishedProduct (Finalizados)
    finished_products = FinishedProduct.objects.all()
    finished_per_day = defaultdict(int)
    for product in finished_products:
        day = product.finished_date
        finished_per_day[day] += product.quantity

    # Coletar os dados brutos do banco de dados para Production (Produção)
    productions = Production.objects.all()
    produced_per_day = defaultdict(int)
    for production in productions:
        day = production.production_date
        produced_per_day[day] += production.quantity

    # Coletar os dados brutos do banco de dados para SalesProduct (Vendidos)
    sales_products = SalesProduct.objects.all()
    sold_per_day = defaultdict(int)
    for sale in sales_products:
        day = sale.sale_date
        sold_per_day[day] += sale.quantity
    
    # Coletar os dados brutos do banco de dados para LeftoverProduct (Sobras)
    left_over_products = LeftoverProduct.objects.all()
    left_over_per_day = defaultdict(int)
    for left_over in left_over_products:
        day = left_over.leftover_date
        left_over_per_day[day] += left_over.quantity

    # Coletar todas as datas únicas de todos os dicionários
    all_dates = sorted(set(finished_per_day.keys()).union(produced_per_day.keys()).union(sold_per_day.keys()).union(left_over_per_day.keys()))

    # Separar as chaves e valores para o gráfico
    dates = [day.strftime('%d/%m/%Y') for day in all_dates]
    finished_totals = [finished_per_day[day] for day in all_dates]
    produced_totals = [produced_per_day[day] for day in all_dates]
    sold_totals = [sold_per_day[day] for day in all_dates]
    left_over_totals = [left_over_per_day[day] for day in all_dates]

    # Calcular as somas totais
    total_finished = sum(finished_totals)
    total_produced = sum(produced_totals)
    total_sold = sum(sold_totals)
    total_left_over = sum(left_over_totals)

    # Converter para JSON para passar ao template
    dates_json = json.dumps(dates)
    finished_totals_json = json.dumps(finished_totals)
    produced_totals_json = json.dumps(produced_totals)
    sold_totals_json = json.dumps(sold_totals)
    left_over_totals_json = json.dumps(left_over_totals)

    context = {
        'total_finished': total_finished,
        'total_produced': total_produced,
        'total_sold': total_sold,
        'total_left_over': total_left_over,
        'dates': dates_json,
        'finished_totals': finished_totals_json,
        'produced_totals': produced_totals_json,
        'sold_totals': sold_totals_json,
        'left_over_totals': left_over_totals_json,
    }
    return render(request, 'dashboard.html', context)
