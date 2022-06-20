from django.db.models import Q
from django.shortcuts import redirect, render
from django_tables2 import RequestConfig
from django_tables2.export import TableExport
from rest_framework import permissions
from rest_framework import serializers
from rest_framework import viewsets

from main_app.models import Package, Courier, CStatus
from main_app.tables import CourierWayBillTable, CourierTable


class CourierSerializer(serializers.ModelSerializer):
    status_mapping = serializers.JSONField(initial={item.description: "" for item in CStatus.objects.all()})
    track_details_div = serializers.JSONField(initial={"tag": "", "attribute": "", "value": ""})
    status_div = serializers.JSONField(initial={"tag": "", "attribute": "", "value": ""})
    date_div = serializers.JSONField(initial={"tag": "", "attribute": "", "value": ""})
    time_div = serializers.JSONField(initial={"tag": "", "attribute": "", "value": ""})
    location_div = serializers.JSONField(initial={"tag": "", "attribute": "", "value": ""})

    class Meta:
        model = Courier
        fields = '__all__'


class CourierViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Courier.objects.all()
    serializer_class = CourierSerializer
    permission_classes = [permissions.IsAuthenticated]


def couriers_list(request):
    context = {}
    couriers = Courier.objects.all()
    table = CourierTable(couriers)
    context["table"] = table
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    export_format = request.GET.get('_export', None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table)
        f_name = "couriers_list." + export_format
        return exporter.response(f_name)
    return render(request, "couriers_list.html", context)


def couriers_waybill(request, id):
    context = {}
    if not request.user.is_authenticated:
        return redirect('api-auth/login')
    else:
        packages = Package.objects.filter(~Q(status__description="Canceled"),courier__id=id)
        price_list = [item.price for item in packages]
        price = 0
        for item in price_list:
            price += float(item)
        context['price'] = price
        table = CourierWayBillTable(packages)
        context["table"] = table
        RequestConfig(request, paginate={"per_page": 25}).configure(table)
        export_format = request.GET.get('_export', None)
        if TableExport.is_valid_format(export_format):
            exporter = TableExport(export_format, table)
            f_name = "CourierWayBill." + export_format
            return exporter.response(f_name)
        return render(request, "couriers_waybill.html", context)
