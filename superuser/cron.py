from datetime import datetime, timedelta
from . import models
from django.db.models import Count, Sum
from django.contrib import messages
from django.shortcuts import redirect
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

def setSalesPersonCommission():
    this_first = datetime.now().date().replace(day=1)
    prev_last_date = this_first - timedelta(days=1)
    salesCommisions = models.SalesOrderHeader.objects.filter(sales_order_date__year=prev_last_date.strftime(
        "%Y"), sales_order_date__month=prev_last_date.strftime("%m")).values('sales_person_id', 'sales_person__salesperson_name').annotate(Sum('total_amount'))
    models.SalesPersonCommissions.objects.filter(
        month=prev_last_date.strftime("%Y-%m")).delete()
    commission_details = []
    for sales_commision in salesCommisions:
        commission_percentage = models.SalesPersonSlabs.objects.filter(sales_person_id=sales_commision['sales_person_id'], slab__from_range__lt=sales_commision['total_amount__sum'], slab__to_range__gte=sales_commision['total_amount__sum']).first().percentage if models.SalesPersonSlabs.objects.filter(sales_person_id=sales_commision['sales_person_id'], slab__from_range__lt=sales_commision['total_amount__sum'], slab__to_range__gte=sales_commision['total_amount__sum']).first() is not None else 0
        commission_details.append(models.SalesPersonCommissions(month=prev_last_date.strftime("%Y-%m"), commission=sales_commision['total_amount__sum'] * Decimal((commission_percentage / 100)), sales_person_id=sales_commision['sales_person_id']))
    models.SalesPersonCommissions.objects.bulk_create(commission_details)
    # messages.success(request, 'Last Month Sales Commission Updated.')
    # return redirect('salesCommissionReports')
    print('Hello')
    logger.info("Cron Job was Called")
