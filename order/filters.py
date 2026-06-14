import django_filters

from .models import Order


class OrderFilter(django_filters.FilterSet):
    min_amount = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="gte"
    )
    max_amount = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="lte"
    )
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="date__gte"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="date__lte"
    )

    status = django_filters.ChoiceFilter(choices=Order.STATUS_CHOICES)
    payment_method = django_filters.ChoiceFilter(choices=Order.PAYMENT_METHOD_CHOICES)

    class Meta:
        model = Order
        fields = {
            "status": ["exact"],
            "payment_method": ["exact"],
            "is_paid": ["exact"],
            "is_pos_order": ["exact"],
            "user": ["exact"],
        }
