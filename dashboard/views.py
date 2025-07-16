from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
from django.utils.dateparse import parse_date
from datetime import datetime

from core.decorators import group_required_any

from production.models import Production
from finished.models import FinishedProduct
from sales.models import SalesProduct, LeftoverProduct
from products.models import Product
from collections import defaultdict
import json

from core.decorators import staff_required

@group_required_any(["ADM", "ALL", "Atendimento", "Cozinha"])
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

    context.update(get_product_daily_summary_data())

    return render(request, 'dashboard.html', context)

def get_product_daily_summary_data():
    from collections import defaultdict
    from datetime import datetime
    import json

    data = defaultdict(lambda: defaultdict(lambda: {
        "produced": 0,
        "finished": 0,
        "sold": 0,
        "left_over": 0,
    }))

    for p in Production.objects.select_related("product"):
        key = p.production_date.strftime('%d/%m/%Y')
        data[p.product.name][key]["produced"] += p.quantity

    for f in FinishedProduct.objects.select_related("product"):
        key = f.finished_date.strftime('%d/%m/%Y')
        data[f.product.name][key]["finished"] += f.quantity

    for s in SalesProduct.objects.select_related("product"):
        key = s.sale_date.strftime('%d/%m/%Y')
        data[s.product.name][key]["sold"] += s.quantity

    for l in LeftoverProduct.objects.select_related("product"):
        key = l.leftover_date.strftime('%d/%m/%Y')
        data[l.product.name][key]["left_over"] += l.quantity

    # Coletar todas as datas únicas
    all_dates = sorted({
        date for product_data in data.values()
        for date in product_data.keys()
    }, key=lambda d: datetime.strptime(d, '%d/%m/%Y'))

    # Montar datasets
    def build(metric):
        return {
            product: [
                data[product][date][metric] if date in data[product] else 0
                for date in all_dates
            ]
            for product in data.keys()
        }

    raw_datasets = {
        "produced": build("produced"),
        "finished": build("finished"),
        "sold": build("sold"),
        "left_over": build("left_over"),
    }

    # Filtrar produtos com movimentação
    filtered_products = []
    for product in data.keys():
        total = sum(raw_datasets["produced"].get(product, [])) + \
                sum(raw_datasets["finished"].get(product, [])) + \
                sum(raw_datasets["sold"].get(product, [])) + \
                sum(raw_datasets["left_over"].get(product, []))
        if total > 0:
            filtered_products.append(product)

    # Refiltrar datasets
    datasets = {
        metric: {
            product: values
            for product, values in data.items()
            if product in filtered_products
        }
        for metric, data in raw_datasets.items()
    }

    return {
        "product_dates": json.dumps(all_dates),
        "product_list": json.dumps(filtered_products),
        "produced_by_product": json.dumps(datasets["produced"]),
        "finished_by_product": json.dumps(datasets["finished"]),
        "sold_by_product": json.dumps(datasets["sold"]),
        "left_over_by_product": json.dumps(datasets["left_over"]),
    }
