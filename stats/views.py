from datetime import timedelta

from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from order.models import Order, OrderItem
from product.models import Category, Product


class DashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can view dashboard stats."}, status=403
            )

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)

        # KPIs
        today_sales = (
            Order.objects
            .filter(created_at__gte=today_start, created_at__lte=now)
            .exclude(status="cancelled")
            .aggregate(total=Sum("total_amount"))["total"]
            or 0.00
        )

        yesterday_sales = (
            Order.objects
            .filter(created_at__gte=yesterday_start, created_at__lt=today_start)
            .exclude(status="cancelled")
            .aggregate(total=Sum("total_amount"))["total"]
            or 0.00
        )

        if yesterday_sales > 0:
            diff_pct = round(
                ((float(today_sales) - float(yesterday_sales)) / float(yesterday_sales))
                * 100
            )
            sales_trend = "up" if diff_pct >= 0 else "down"
            sales_hint = (
                f"{'↑' if diff_pct >= 0 else '↓'} {abs(diff_pct)}% vs yesterday"
            )
        else:
            sales_trend = "up" if today_sales > 0 else "neutral"
            sales_hint = "No sales yesterday"

        today_orders = (
            Order.objects
            .filter(created_at__gte=today_start, created_at__lte=now)
            .exclude(status="cancelled")
            .count()
        )

        pending_orders = Order.objects.filter(status="pending").count()
        orders_hint = f"{pending_orders} pending"

        low_stock_count = Product.objects.filter(stock__lt=5).count()
        low_stock_hint = "Action needed" if low_stock_count > 0 else "All good"

        live_animals_count = (
            Product.objects.filter(
                Q(category__name__icontains="live")
                | Q(category__name__icontains="animal")
            ).aggregate(total_stock=Sum("stock"))["total_stock"]
            or 0
        )

        live_categories_count = Category.objects.filter(
            Q(name__icontains="live") | Q(name__icontains="animal")
        ).count()
        live_animals_hint = f"{live_categories_count} categories"

        # Recent Orders (limit 5)
        recent_orders_qs = Order.objects.only(
            "order_id", "full_name", "total_amount", "status", "created_at"
        ).order_by("-created_at")[:5]

        recent_orders = []
        for order in recent_orders_qs:
            time_diff = now - order.created_at
            if time_diff.days > 0:
                time_str = f"{time_diff.days}d ago"
            elif time_diff.seconds >= 3600:
                time_str = f"{time_diff.seconds // 3600}h ago"
            elif time_diff.seconds >= 60:
                time_str = f"{time_diff.seconds // 60}m ago"
            else:
                time_str = "just now"

            recent_orders.append({
                "order_id": order.order_id,
                "full_name": order.full_name,
                "total_amount": float(order.total_amount),
                "status": order.status,
                "time_ago": time_str,
            })

        return Response({
            "kpis": {
                "today_sales": {
                    "value": f"Rs {int(today_sales):,}" if today_sales >= 1 else "Rs 0",
                    "hint": sales_hint,
                    "trend": sales_trend,
                },
                "today_orders": {
                    "value": str(today_orders),
                    "hint": orders_hint,
                    "trend": "up" if today_orders > 0 else "neutral",
                },
                "low_stock_items": {
                    "value": str(low_stock_count),
                    "hint": low_stock_hint,
                    "trend": "down" if low_stock_count > 0 else "neutral",
                },
                "live_animals": {
                    "value": str(live_animals_count),
                    "hint": live_animals_hint,
                    "trend": "neutral",
                },
            },
            "recent_orders": recent_orders,
        })


class SalesChartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can view dashboard stats."}, status=403
            )

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        sales_chart = []
        for i in range(6, -1, -1):
            day_date = today_start - timedelta(days=i)
            day_end = day_date + timedelta(days=1)
            day_name = day_date.strftime("%a")

            day_sales = (
                Order.objects
                .filter(created_at__gte=day_date, created_at__lt=day_end)
                .exclude(status="cancelled")
                .aggregate(total=Sum("total_amount"))["total"]
                or 0.00
            )

            sales_chart.append({"d": day_name, "v": float(day_sales)})

        return Response(sales_chart)


class CategoryChartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can view dashboard stats."}, status=403
            )

        category_sales = (
            OrderItem.objects
            .exclude(order__status="cancelled")
            .values("product__category__name")
            .annotate(total_value=Sum("price"))
            .order_by("-total_value")[:5]
        )

        category_chart = []
        for cs in category_sales:
            cat_name = cs["product__category__name"] or "Uncategorized"
            category_chart.append({
                "name": cat_name,
                "v": float(cs["total_value"] or 0),
            })

        if not category_chart:
            categories = Category.objects.all()[:5]
            for cat in categories:
                category_chart.append({
                    "name": cat.name,
                    "v": float(Product.objects.filter(category=cat).count() * 100),
                })

        return Response(category_chart)


class AlertsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can view dashboard stats."},
                status=403,
            )

        alerts = []

        # ------------------------------------------------------------------ #
        # 1. Low stock alert
        # ------------------------------------------------------------------ #
        low_stock_count = Product.objects.filter(stock__lte=10).count()

        if low_stock_count > 0:
            alerts.append({
                "type": "danger",
                "message": (
                    f"{low_stock_count} item{'s' if low_stock_count > 1 else ''} "
                    "below minimum stock"
                ),
            })
        else:
            alerts.append({
                "type": "success",
                "message": "All items are in stock",
            })

        # ------------------------------------------------------------------ #
        # 2. Dynamic sales trend alert  (this week vs last week)
        # ------------------------------------------------------------------ #
        CONFIRMED_STATUSES = ["processing", "shipped", "delivered"]

        now = timezone.now()
        this_week_start = now - timedelta(days=7)
        last_week_start = now - timedelta(days=14)

        this_week_sales = (
            Order.objects.filter(
                created_at__gte=this_week_start,
                status__in=CONFIRMED_STATUSES,
            ).aggregate(total=Sum("total_amount"))["total"]
            or 0
        )

        last_week_sales = (
            Order.objects.filter(
                created_at__gte=last_week_start,
                created_at__lt=this_week_start,
                status__in=CONFIRMED_STATUSES,
            ).aggregate(total=Sum("total_amount"))["total"]
            or 0
        )

        if last_week_sales == 0:
            if this_week_sales > 0:
                alerts.append({
                    "type": "info",
                    "message": "First sales recorded this week!",
                })
            else:
                alerts.append({
                    "type": "info",
                    "message": "No sales data available yet",
                })
        else:
            change_pct = ((this_week_sales - last_week_sales) / last_week_sales) * 100
            abs_pct = abs(round(change_pct))

            if change_pct >= 5:
                alerts.append({
                    "type": "success",
                    "message": f"Sales up {abs_pct}% this week",
                })
            elif change_pct <= -5:
                alerts.append({
                    "type": "danger",
                    "message": f"Sales down {abs_pct}% this week",
                })
            else:
                alerts.append({
                    "type": "info",
                    "message": f"Sales stable this week (\u00b1{abs_pct}%)",
                })

        # ------------------------------------------------------------------ #
        # 3. Pending orders alert
        # ------------------------------------------------------------------ #
        pending_count = Order.objects.filter(status="pending").count()

        if pending_count > 0:
            alerts.append({
                "type": "warning",
                "message": (
                    f"{pending_count} order{'s' if pending_count > 1 else ''} "
                    "awaiting processing"
                ),
            })

        # ------------------------------------------------------------------ #
        # 4. Unpaid (COD) orders alert
        # ------------------------------------------------------------------ #
        unpaid_count = Order.objects.filter(
            is_paid=False,
            status__in=CONFIRMED_STATUSES,
        ).count()

        if unpaid_count > 0:
            alerts.append({
                "type": "warning",
                "message": (
                    f"{unpaid_count} confirmed order{'s' if unpaid_count > 1 else ''} "
                    "with pending payment"
                ),
            })

        return Response(alerts)
