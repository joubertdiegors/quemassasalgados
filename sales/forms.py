from django import forms
from products.models import Product
from .models import SalesOrder, SalesProduct

class SalesOrderForm(forms.Form):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        label="Produtos"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for product in self.fields['products'].queryset:
            self.fields[f'quantity_{product.id}'] = forms.IntegerField(
                min_value=1,
                initial=1,
                required=False,
                label=f'Quantidade para {product.name}'
            )

    def clean(self):
        cleaned_data = super().clean()
        selected_products = cleaned_data.get('products', [])
        
        for product in selected_products:
            quantity_field = f'quantity_{product.id}'
            quantity = cleaned_data.get(quantity_field)
            if not quantity:
                self.add_error(quantity_field, 'Este campo é obrigatório para o produto selecionado.')

        return cleaned_data

class SalesOrderUpdateForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        label="Produtos"
    )

    class Meta:
        model = SalesOrder
        fields = ['sale_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            selected_products = self.instance.sales_products.all()
            self.fields['products'].initial = [prod.product for prod in selected_products]
            
            for product in self.fields['products'].queryset:
                field_name = f'quantity_{product.id}'
                initial_quantity = next((prod.quantity for prod in selected_products if prod.product.id == product.id), 1)
                self.fields[field_name] = forms.IntegerField(
                    initial=initial_quantity,
                    min_value=1,
                    required=False,
                    label=f'Quantidade para {product.name}'
                )

    def clean(self):
        cleaned_data = super().clean()
        selected_products = cleaned_data.get('products', [])
        
        for product in selected_products:
            quantity_field = f'quantity_{product.id}'
            quantity = cleaned_data.get(quantity_field)
            if not quantity:
                self.add_error(quantity_field, 'Este campo é obrigatório para o produto selecionado.')

        return cleaned_data
