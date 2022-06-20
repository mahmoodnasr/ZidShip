from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import permissions
from rest_framework import serializers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from main_app.helper import class_for_name
from main_app.models import Package, Courier, CStatus


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PackageSerializer, self).__init__(*args, **kwargs)
        self.fields['courier'].queryset = Courier.objects.filter(is_active=True)


class PackageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAuthenticated]


# For the Dashboard and track all the similar package status
def package_by_status(request,status_name=None):
    context = {}
    from main_app.tables import PackagesTable
    status = status_name if status_name else request.GET['status']
    packages = Package.objects.filter(status__description=status).order_by('date_created')
    context['table'] = PackagesTable(packages)
    context['status'] = status
    return render(request, "packages_by_status_table.html", context)


# Tracking functions
def track_package(request):
    package_id = request.POST.get('id', None)
    package = Package.objects.get(pk=package_id)
    if package.courier.outer_script_path:
        class_obj = class_for_name(package.courier.outer_script_path)
        b = class_obj(package)
        result = b.Get_Tracking_Data()
        html = "<p>" + result + "</p>"
    else:
        status, data = track_package_core(package)
        if not status:
            html = "<p>" + data + "</p>"
        else:
            html = "<ul>"
            for item in data:
                html += f"<li>Package {item['status']} located in {item['location']} on {item['date']} at {item['time']} </li>"
            html += "</ul>"
    return JsonResponse({"html": html})


# Tracking Core function - to automate it with celery in the V.2
def track_package_core(package):
    from main_app.api.trackers import Tracker
    try:
        b = Tracker(package)
        result = b.Get_Tracking_Data()
        package.status = CStatus.objects.get(description=result['status'])
        package.save()
        return 1, result['data']
    except:
        import traceback
        print(traceback.format_exc())
        return 0, traceback.format_exc()


def cancel_package(request, id):
    if not request.user.is_authenticated:
        return HttpResponse("You are not allowed")
    else:
        user = request.user
        if user.is_superuser or user.is_staff:
            try:
                package = Package.objects.get(id=id)
                package.status = CStatus.objects.get(description="Canceled")
                package.save()
                return HttpResponse("Changed Successfully")
            except:
                return HttpResponse("Package cannot be found")
        else:
            return HttpResponse("You are not allowed")
