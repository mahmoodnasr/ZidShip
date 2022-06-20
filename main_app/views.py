from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django_tables2.config import RequestConfig
from django_tables2.export import TableExport

from .helper import class_for_name
from .models import Package, CStatus, Courier
from .tables import PackagesTable


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('api-auth/login')
    else:
        from .chart import charts
        context = {}
        context['showCharts'] = True
        context.update(charts(request))

        packages = Package.objects.all().order_by('date_created')
        table = PackagesTable(packages)
        count = packages.count()
        context["count"] = count
        if count > 0:
            context["table"] = table
        else:
            context["empty"] = True
        RequestConfig(request, paginate={"per_page": 25}).configure(table)
        export_format = request.GET.get('_export', None)
        if TableExport.is_valid_format(export_format):
            exporter = TableExport(export_format, table)
            f_name = "packages." + export_format
            return exporter.response(f_name)
        return render(request, "index.html", context)
