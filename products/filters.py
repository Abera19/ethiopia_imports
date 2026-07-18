import django_filters
from django import forms
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        empty_label='All Categories',
        field_name='category'
    )

    min_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Min Price (ETB)',
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Min'})
    )

    max_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Max Price (ETB)',
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Max'})
    )

    q = django_filters.CharFilter(
        method='filter_search',
        label='Search',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Search products...'})
    )

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'q']

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                models.Q(title__icontains=value) |
                models.Q(description__icontains=value) |
                models.Q(source__icontains=value)
            )
        return queryset