from django.urls import path, include, re_path
from rest_framework import routers

from . import views
from .api.Client import ClientViewSet
from .api.Couriers import CourierViewSet,couriers_list,couriers_waybill
from .api.Packages import PackageViewSet,cancel_package,package_by_status,track_package
from .api.Status import CStatusViewSet

router = routers.SimpleRouter()

router.register(r'couriers', CourierViewSet)
router.register(r'packages', PackageViewSet)
router.register(r'cstatuses', CStatusViewSet)
router.register(r'clients', ClientViewSet)

urlpatterns = [
    path(r'', views.dashboard, name='Dashboard'),
    path(r'', include((router.urls, 'main_app'))),

    path(r'packages/cancel/<int:id>/', cancel_package, name='cancel_package'),

    path(r'list/couriers/', couriers_list, name='couriers_list'),
    path(r'couriers/waybill/<int:id>/', couriers_waybill, name='couriers_waybill'),

    re_path('package/status/', package_by_status, name='package_by_status'),
    path(r'package/status/<slug:status_name>', package_by_status),

    re_path('package/track/', track_package, name='track_package'),
    path(r'package/<int:id>/track/', track_package)
]
