"""
This file contains Tables as in django-tables2
"""

import django_tables2 as tables
from django_tables2.export.views import ExportMixin
from django.utils.html import mark_safe


class PackagesTable(ExportMixin, tables.Table):
    """Show a list of Packages as a table"""
    name = tables.TemplateColumn("""<a href="{% url 'main_app:package-detail' pk=record.pk %}">{{ record.name }}</a>""",
                                 verbose_name="Package Name")
    track_number = tables.Column(verbose_name="Track Number")
    courier = tables.TemplateColumn(
        """<a href="{% url 'main_app:courier-detail' pk=record.courier.pk %}">{{ record.courier.name }}</a>""")
    client = tables.TemplateColumn(
        """<a href="{% url 'main_app:client-detail' pk=record.client.id %}">{{ record.client.username }}</a>""")
    source = tables.Column(verbose_name="Source")
    destination = tables.Column(verbose_name="Destination")
    status = tables.TemplateColumn(
        '<span class="dot dot-{{record.status.color}}" title="{{ record.status.description }}">', verbose_name="Status")
    date_created = tables.DateTimeColumn(verbose_name="Added On", format='M d Y, h:i')
    actions = tables.TemplateColumn(template_name="tables_actions/packages_table_actions.html", verbose_name="Actions",
                                    orderable=False, exclude_from_export=True)

    def value_status(self, value, record):
        return record.status.description

    def value_client(self, value, record):
        return record.client.username

    def value_courier(self, value, record):
        return record.courier.name

    class Meta:
        fields = ['name', 'track_number', 'courier', 'client', 'source', 'destination', 'status', 'date_created']
        attrs = {"class": "table table-data2"}


class CourierTable(ExportMixin, tables.Table):
    """Show a list of CourierWayBil as a table"""
    name = tables.TemplateColumn(
        """<a href="{% url 'main_app:courier-detail' pk=record.pk %}">{{ record.name }}</a>""")
    is_active = tables.BooleanColumn(verbose_name="Is Active")
    actions = tables.TemplateColumn(template_name="tables_actions/courier_table_actions.html", verbose_name="Actions",
                                    orderable=False, exclude_from_export=True)
    class Meta:
        fields = ['name', 'is_active', 'actions']
        attrs = {"class": "table table-data2"}


class CourierWayBillTable(ExportMixin, tables.Table):
    """Show a list of CourierWayBil as a table"""
    name = tables.TemplateColumn(
        """<a href="{% url 'main_app:package-detail' pk=record.pk %}">{{ record.name }}</a>""")
    client = tables.Column(verbose_name="Client")
    price = tables.Column(verbose_name="Price")
    source = tables.Column(verbose_name="Source")
    destination = tables.Column(verbose_name="Destination")
    date_created = tables.Column(verbose_name="Created")

    class Meta:
        fields = ['name', 'client', 'price', 'source', 'destination', 'date_created']
        attrs = {"class": "table table-data2"}
