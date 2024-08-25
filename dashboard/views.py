from django.shortcuts import render
from production.models import Production
from finished.models import FinishedProduct
from collections import defaultdict
from datetime import datetime
import json

def dashboard_view(request):
    # Coletar os dados brutos do banco de dados para FinishedProduct
    finished_products = FinishedProduct.objects.all()
    finished_per_day = defaultdict(int)
    for product in finished_products:
        day = product.finished_date
        finished_per_day[day] += product.quantity

    # Coletar os dados brutos do banco de dados para Production
    productions = Production.objects.all()
    produced_per_day = defaultdict(int)
    for production in productions:
        day = production.production_date
        produced_per_day[day] += production.quantity

    # Coletar todas as datas únicas de ambos os dicionários
    all_dates = sorted(set(finished_per_day.keys()).union(produced_per_day.keys()))

    # Separar as chaves e valores para o gráfico
    dates = [day.strftime('%d/%m/%Y') for day in all_dates]
    finished_totals = [finished_per_day[day] for day in all_dates]
    produced_totals = [produced_per_day[day] for day in all_dates]

    # Calcular as somas totais
    total_finished = sum(finished_totals)
    total_produced = sum(produced_totals)

    # Converter para JSON para passar ao template
    dates_json = json.dumps(dates)
    finished_totals_json = json.dumps(finished_totals)
    produced_totals_json = json.dumps(produced_totals)

    context = {
        'total_finished': total_finished,
        'total_produced': total_produced,
        'dates': dates_json,
        'finished_totals': finished_totals_json,
        'produced_totals': produced_totals_json,
    }
    return render(request, 'dashboard.html', context)
