import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(
        field_name="category_id"
    )

    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte"
    )

    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte"
    )

    in_stock = django_filters.BooleanFilter(
        method="filter_in_stock"
    )

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)

        return queryset.filter(stock=0)

    class Meta:
        model = Product
        fields = [
            "category",
            "min_price",
            "max_price",
            "in_stock",
        ]