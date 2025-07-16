from django import forms
from .models import Product, ProductCategory, Kit, KitOption
from django.forms import inlineformset_factory

class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name', 'parent', 'show_on_website', 'description']
        labels = {
            'name': 'Nome da categoria',
            'parent': 'Categoria pai (opcional)',
            'show_on_website': 'Mostrar no site?',
            'description': 'Descrição para o site',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'show_on_website': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'description',
            'stock_quantity',
            'show_on_website',
            'use_in_production',
            'image',
        ]
        labels = {
            'name': 'Nome do Produto',
            'category': 'Categoria',
            'description': 'Descrição',
            'stock_quantity': 'Estoque',
            'show_on_website': 'Exibir no site',
            'use_in_production': 'Usar na produção',
            'image': 'Imagem',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'show_on_website': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'use_in_production': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        categories = ProductCategory.objects.select_related('parent').all()

        def get_label(cat):
            return f"{cat.parent.name} > {cat.name}" if cat.parent else cat.name

        # Cria lista ordenada de tuplas (id, label)
        sorted_choices = sorted(
            [(cat.id, get_label(cat)) for cat in categories],
            key=lambda x: x[1].lower()  # ordena alfabeticamente, ignorando maiúsculas/minúsculas
        )

        self.fields['category'].choices = [('', '---------')] + sorted_choices

class KitForm(forms.ModelForm):
    class Meta:
        model = Kit
        fields = ['name', 'description', 'image', 'is_active', 'show_on_website']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_on_website': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Formset para KitOption relacionado ao Kit
KitOptionFormSet = inlineformset_factory(
    Kit,
    KitOption,
    fields=['category', 'max_choices'],
    extra=1,
    widgets={
        'category': forms.Select(attrs={'class': 'form-select'}),
        'max_choices': forms.NumberInput(attrs={'class': 'form-control'}),
    }
)
