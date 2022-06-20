from django.contrib import admin
from .models import Package, Courier, CStatus


class PackageAdmin(admin.ModelAdmin):
    list_display = ('track_number', 'name', 'courier', 'client', 'status',)


class CourierAdmin(admin.ModelAdmin):
    list_display = ('name',)


class CStatusAdmin(admin.ModelAdmin):
    list_display = ('description',)


admin.site.register(Package, PackageAdmin)
admin.site.register(Courier, CourierAdmin)
admin.site.register(CStatus, CStatusAdmin)
