from django.shortcuts import render
from production.models import Production
from finished.models import FinishedProduct
from django.db.models import Sum
from collections import defaultdict
from datetime import datetime
import json  # Adicione essa importação

def dashboard_view(request):
    # Coletar os dados brutos do banco de dados
    finished_products = FinishedProduct.objects.all()

    # Criar um dicionário para armazenar as somas por dia
    finished_per_day = defaultdict(int)

    for product in finished_products:
        day = product.finished_date  # Extrai apenas a data (sem hora)
        finished_per_day[day] += product.quantity

    # Separar as chaves e valores para o gráfico
    dates = [day.strftime('%d/%m/%Y') for day in sorted(finished_per_day.keys())]
    totals = [finished_per_day[day] for day in sorted(finished_per_day.keys())]

    # Calcular a soma total dos produtos finalizados
    total_finished = sum(totals)

    # Converter para JSON para passar ao template
    dates_json = json.dumps(dates)
    totals_json = json.dumps(totals)

    context = {
        'total_production': Production.objects.aggregate(total_units=Sum('quantity'))['total_units'] or 0,
        'total_finished': total_finished,
        'dates': dates_json,  # Passa como string JSON
        'totals': totals_json,  # Passa como string JSON
    }
    return render(request, 'dashboard.html', context)
