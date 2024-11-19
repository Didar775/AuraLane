from django import forms
from .models import Item, Review


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'name',
            'description',
            'code',
            'buy_price',
            'sale_price',
            'min_price',
            'weight',
            'href',
            'category',
            'tags',
            'sale',
            'in_stock',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'sale': forms.Select(attrs={'class': 'form-select'}),
            'in_stock': forms.CheckboxInput(),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'pros', 'cons']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'pros': forms.Textarea(attrs={'rows': 3}),
            'cons': forms.Textarea(attrs={'rows': 3}),
        }
