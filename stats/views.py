import calendar
from datetime import date, timedelta, datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, F
from django.db.models.functions import ExtractWeek, ExtractMonth, ExtractDay, ExtractYear
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import generics
from user_visit.models import UserVisit

from accounts.models import User
from orders.models import Order, Shipment, TrackingActivities, OrderItems, Carrier
from products.models import Product


def get_first_date_of_current_month(year, month):
    """Return the first date of the month.

    Args:
        year (int): Year
        month (int): Month

    Returns:
        date (datetime): First date of the current month
    """
    first_date = datetime(year, month, 1)
    return first_date.strftime("%V")


def get_last_date_of_month(year, month):
    """Return the last date of the month.

    Args:
        year (int): Year, i.e. 2022
        month (int): Month, i.e. 1 for January

    Returns:
        date (datetime): Last date of the current month
    """

    if month == 12:
        last_date = datetime(year, month, 31)
    else:
        last_date = datetime(year, month + 1, 1) + timedelta(days=-1)

    return last_date.strftime("%V")


class Today(LoginRequiredMixin, generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        data = {"cost": 0}
        visits = UserVisit.objects.filter(timestamp__date__gte=timezone.localdate()).count()
        orders = Order.objects.filter(user=request.user, created_at__gte=timezone.localdate().today())
        id_orders = []
        for order in orders:
            if not int(order.id) in id_orders:
                id_orders.append(int(order.id))
                order.shipment = Shipment.objects.filter(order__id=order.id).last()
                order.activity = TrackingActivities.objects.filter(order__id=order.id).last()
                order.items = OrderItems.objects.filter(
                    order=int(order.id))
                for item in order.items:
                    if Product.objects.filter(
                            id=item.original_product_id).count() > 0:
                        item.linked_item = Product.objects.filter(
                            id=item.original_product_id)[0]

                        data.update({
                            "cost": (item.linked_item.price * item.quantity) + order.estimated_shipment_cost
                        })

        data.update({
            "day": datetime.today().day,
            "visits": visits,
            "orders": orders.count()
        })

        return JsonResponse(data)


class Daily(LoginRequiredMixin, generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        data = {}
        visits = UserVisit.objects.filter(timestamp__date__gte=timezone.localdate()).count()
        orders = Order.objects.filter(user=request.user)
        day = orders.annotate(day_num=ExtractDay('created_at')).values('day_num'). \
            annotate(count=Count('day_num')).annotate(Sum('estimated_shipment_cost')).annotate(
            c=Count('pk')
        ).values(
            "day_num", "estimated_shipment_cost", "c"
        )

        id_orders = []
        for order in orders:
            if not int(order.id) in id_orders:
                id_orders.append(int(order.id))
                order.shipment = Shipment.objects.filter(order__id=order.id).last()
                order.activity = TrackingActivities.objects.filter(order__id=order.id).last()
                order.items = OrderItems.objects.filter(
                    order=int(order.id))
                for item in order.items:
                    if Product.objects.filter(
                            id=item.original_product_id).count() > 0:
                        item.linked_item = Product.objects.filter(
                            id=item.original_product_id)[0]

                        data.update({
                            "prix": (item.linked_item.price * item.quantity) + order.estimated_shipment_cost
                        })

        data.update({
            'per_day': list(day),
            'visits': visits,
        })

        return JsonResponse(data)


class Weekly(LoginRequiredMixin, generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        data = {}
        query = Order.objects.filter(user=request.user)
        week_start = timezone.now().date()
        week_start -= timedelta(days=week_start.weekday())
        week_end = week_start + timedelta(days=7)

        week = query.filter(created_at__range=[week_start, week_end])
        id_orders = []
        s = 0
        for order in week:
            if not int(order.id) in id_orders:
                id_orders.append(int(order.id))
                order.shipment = Shipment.objects.filter(order__id=order.id).last()
                order.activity = TrackingActivities.objects.filter(order__id=order.id).last()
                order.items = OrderItems.objects.filter(
                    order=int(order.id))
                for item in order.items:
                    if Product.objects.filter(
                            id=item.original_product_id).count() > 0:
                        item.linked_item = Product.objects.filter(
                            id=item.original_product_id)[0]

                        s += (item.linked_item.price * item.quantity) + order.estimated_shipment_cost

        days = []
        id_orders = []
        print(week_start, week_end)
        for i in range((week_end - week_start).days + 1):
            current_date = week_start + timedelta(days=i)
            w = query.filter(created_at__gte=current_date)

            days.append({
                "name": current_date.strftime("%A"),
                "day": current_date,
                "count": w.count()
            })
            id_orders.append(w.count())

        data.update({
            "this_week": s,
            "days": days,
            "chart": id_orders
        })

        total = query.count() if query else 1
        filt = query.filter(created_at__range=[week_start, week_end]).count()
        try:
            perc = round((filt * 100) / total, 2)
        except ZeroDivisionError:
            perc = 0

        data.update({
            'perc': perc
        })

        return JsonResponse(data)


class Monthly(LoginRequiredMixin, generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        data = {}
        query = Order.objects.filter(user=request.user)

        weeks = []
        datet = datetime.today()
        year, months = datet.year, datet.month
        month = query.filter(created_at__month__gte=months).count()
        start_week = int(get_first_date_of_current_month(year, months))
        end_week = int(get_last_date_of_month(year, months))
        chart_weeks = []
        chart_data = []
        for i in range(start_week, end_week + 1):
            w = query.filter(created_at__week=i)
            cost = w.values(
                'estimated_shipment_cost'
            ).aggregate(Sum('estimated_shipment_cost'))
            chart_weeks.append("Week " + str(i))
            chart_data.append(w.count())
            weeks.append({
                "week": i,
                "count": w.count(),
                "cost": cost['estimated_shipment_cost__sum']
            })
            data.update({
                "weeks": weeks,
                "chart_weeks": chart_weeks,
                "chart_data": chart_data,
            })

        total = query.count() if query else 1
        filt = query.filter(created_at__month=datetime.now().month).count()

        fil = query.filter(created_at__month=datetime.now().month - 1).count()
        try:
            perc = round((filt * 100) / total, 2)
        except ZeroDivisionError:
            perc = 0
        try:
            per = round((fil * 100) / total, 2)
        except ZeroDivisionError:
            per = 0

        if per < perc:
            data.update({
                "status": "+" + str(perc - per)
            })
        else:
            data.update({
                "status": "-" + str(per - perc)
            })

        data.update({
            'this_month': month,
            'perc': perc
        })

        return JsonResponse(data)


class Yearly(LoginRequiredMixin, generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        item = order = None
        data = {}
        query = Order.objects.filter(user=request.user)
        year = query.annotate(
            year_num=ExtractYear('created_at')  # sets week number for each row
        ).values(
            'year_num'
        ).annotate(
            count=Count('year_num')
        ).annotate(Sum('estimated_shipment_cost'))

        months = []
        for i in range(1, 13):
            m = query.filter(created_at__month__gte=i)
            id_orders = []
            for order in m:
                if not int(order.id) in id_orders:
                    id_orders.append(int(order.id))
                    order.shipment = Shipment.objects.filter(order__id=order.id).last()
                    order.activity = TrackingActivities.objects.filter(order__id=order.id).last()
                    order.items = OrderItems.objects.filter(
                        order=int(order.id))
                    for item in order.items:
                        if Product.objects.filter(
                                id=item.original_product_id).count() > 0:
                            item.linked_item = Product.objects.filter(
                                id=item.original_product_id)[0]

                            months.append({
                                "month": i,
                                "count": m.count(),
                                "cost": (item.linked_item.price * item.quantity) + order.estimated_shipment_cost
                            })

            data.update({
                "months": months
            })

        total = query.count() if query else 1
        filt = query.filter(created_at__year=datetime.now().year).count()
        fil = query.filter(created_at__year=datetime.now().year - 1).count()
        try:
            perc = round((filt * 100) / total, 2)
        except ZeroDivisionError:
            perc = 0
        try:
            per = round((fil * 100) / total, 2)
        except ZeroDivisionError:
            per = 0
        data.update({
            "status": "+" + str(perc - per) if per < perc else "-" + str(per - perc)
        })

        data.update({
            'yearly': list(year),
            'perc': perc
        })

        return JsonResponse(data)


class Dashboard(LoginRequiredMixin, generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        query = Order.objects.filter(user=request.user)
        total_orders = query.all()
        visits = UserVisit.objects.all().count()
        customers = User.objects.filter(groups__name__in=['personnel', 'fournisseur']).count()
        livrer = query.filter(status="OS", substatus__in=['PT', 'IT']).count()
        processing = query.filter(status="OS", substatus__in=['PT', 'IT']).count()
        shipping = query.filter(status="OS", substatus='IT').count()
        new = query.filter(status="NO").count()
        sold = query.filter(status="D").count()
        refunds = query.filter(status="F").count()

        data = {
            'orders': total_orders.count(),
            'customers': customers,
            'visits': visits,
            'livrer': livrer,
            'new': new,
            "sold": sold,
            "refunds": refunds,
            "shipping": shipping,
            "processing": processing,
        }

        id_orders = []
        for order in total_orders:
            if not int(order.id) in id_orders:
                id_orders.append(int(order.id))
                order.shipment = Shipment.objects.filter(order__id=order.id).last()
                order.activity = TrackingActivities.objects.filter(order__id=order.id).last()
                order.items = OrderItems.objects.filter(
                    order=int(order.id))
                for item in order.items:
                    if Product.objects.filter(
                            id=item.original_order_item_id).count() > 0:
                        item.linked_item = Product.objects.filter(
                            id=item.original_order_item_id)[0]

                        data.update({
                            "cost": (item.linked_item.price * item.quantity) + order.estimated_shipment_cost
                        })

        return JsonResponse(data)


class Completed(LoginRequiredMixin, generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        data = {}
        orders = Order.objects.filter(status="D").distinct("children__name")
        items = []
        chart = []
        for order in list(orders):
            order.items = OrderItems.objects.filter(
                order=int(order.id)).distinct()
            for item in order.items:
                items.append({
                    "name": item.name,
                    "quantity": item.quantity,
                    "percentage": round(item.quantity * 100 / len(orders), 2)
                })

        data.update({
            "items": items[:3],
        })

        for i in items:
            chart.append({"name": i['name'], "value": i['quantity']})

        data.update({
            "chart": chart
        })

        return JsonResponse(data, safe=False)


class Status(LoginRequiredMixin, generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        data = {}
        query = Order.objects.filter(user=request.user)
        new = query.filter(status="NO")
        action = query.filter(status="AC")
        shipped = query.filter(status="OS")
        completed = query.filter(status="D")
        problems = query.filter(status="F")

        d = [
            {'new': new.count(), 'perc': round(new.count() * 100 / query.count(), 2)},
            {'action': action.count(), 'perc': round(action.count() * 100 / query.count(), 2)},
            {'shipped': shipped.count(), 'perc': round(shipped.count() * 100 / query.count(), 2)},
            {'completed': completed.count(), 'perc': round(completed.count() * 100 / query.count(), 2)},
            {'problems': problems.count(), 'perc': round(problems.count() * 100 / query.count(), 2)},
        ]

        data.update({
            "data": d
        })

        return JsonResponse(data)


class Total(LoginRequiredMixin, generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        data = {}
        orders = Order.objects.filter()
        d = []
        m = []
        dates = []
        for i in range(1, 28, 2):
            last_month = orders.filter(created_at__month=datetime.now().month - 1, created_at__day=i)
            id_orders = []
            for order in last_month:
                if not int(order.id) in id_orders:
                    id_orders.append(int(order.id))
                    order.shipment = Shipment.objects.filter(order__id=order.id).last()
                    order.activity = TrackingActivities.objects.filter(order__id=order.id).last()
                    order.items = OrderItems.objects.filter(
                        order=int(order.id))
                    for item in order.items:
                        if Product.objects.filter(
                                id=item.original_product_id).count() > 0:
                            item.linked_item = Product.objects.filter(
                                id=item.original_product_id)[0]

                            data.update({
                                "total_month": (item.linked_item.price * item.quantity) + order.estimated_shipment_cost
                            })
            else:
                data.update({
                    "total_month": 0
                })
            last_year = orders.filter(created_at__year=datetime.now().year - 1, created_at__day=i)
            id_orders = []
            for order in last_year:
                if not int(order.id) in id_orders:
                    id_orders.append(int(order.id))
                    order.shipment = Shipment.objects.filter(order__id=order.id).last()
                    order.activity = TrackingActivities.objects.filter(order__id=order.id).last()
                    order.items = OrderItems.objects.filter(
                        order=int(order.id))
                    for item in order.items:
                        if Product.objects.filter(
                                id=item.original_product_id).count() > 0:
                            item.linked_item = Product.objects.filter(
                                id=item.original_product_id)[0]

                            data.update({
                                "total_year": (item.linked_item.price * item.quantity) + order.estimated_shipment_cost
                            })
            else:
                data.update({
                    "total_year": 0
                })
            dates.append(datetime(datetime.now().year, datetime.now().month - 1, i).date())
            d.append(last_month.count())
            m.append(last_year.count())

        data.update({
            "last_month": d,
            "last_year": m,
            "dates": dates
        })

        return JsonResponse(data)


class Shipped(LoginRequiredMixin, generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        data = {}
        orders = Order.objects.filter(user=request.user)
        shipment = Shipment.objects.filter(order__in=orders)
        all_carrier = Carrier.objects.all()
        if shipment.count() > 0:
            s = 0
            for i in shipment:
                s += 1
            target = round(s * 100 / all_carrier.count(), 2)

            data.update({
                "target": target,
            })

        names = []
        q = []
        quantities = {}
        for ship in shipment:
            order = ship.order
            items = OrderItems.objects.filter(order=int(order.id)).distinct()
            for item in items:
                product = Product.objects.get(id=item.original_product.id)
                name = product.name
                quantity = item.quantity
                if name in quantities:
                    quantities[name] += quantity
                else:
                    quantities[name] = quantity

        for name, quantity in quantities.items():
            names.append(name)
            q.append(quantity)

        data.update({
            "chart": names,
            "quantities": q,
        })
        try:
            perc = round(shipment.count() * 100 / orders.count(), 2)
        except ZeroDivisionError:
            perc = 0
        data.update({
            'count': shipment.count(),
            'perc': perc,
        })

        return JsonResponse(data)
