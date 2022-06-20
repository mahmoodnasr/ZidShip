import json

from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import ImproperlyConfigured


class ZidShipGroup(Group):
    GROUP_ADMIN = 'admin'
    GROUP_COURIER = 'courier'
    GROUP_CLIENT = 'client'

    @classmethod
    def get_group_or_raise(cls, group_name):
        try:
            return cls.objects.get(name=group_name)
        except cls.DoesNotExist:
            raise ImproperlyConfigured('You must create the base user groups:(%s,%s,%s)' % (
                cls.GROUP_ADMIN, cls.GROUP_COURIER, cls.GROUP_CLIENT))

    @classmethod
    def admin(cls):
        return cls.get_group_or_raise(cls.GROUP_ADMIN)

    @classmethod
    def courier(cls):
        return cls.get_group_or_raise(cls.GROUP_COURIER)

    @classmethod
    def client(cls):
        return cls.get_group_or_raise(cls.GROUP_CLIENT)

    class Meta:
        proxy = True


class ClientManager(models.Manager):
    def get_query_set(self):
        return super(ClientManager, self).get_query_set().filter(groups__name=ZidShipGroup.GROUP_CLIENT)


class Client(User):
    objects = ClientManager()

    def from_user(self, user):
        self.__dict__ = user.__dict__
        return self

    class Meta:
        proxy = True


class CStatus(models.Model):
    """Constant table of the status available in the system"""
    code = models.AutoField(primary_key=True)
    description = models.CharField(max_length=100)
    color = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return u'%s' % self.description

    class Meta:
        db_table = 'C_Status'

class Courier(models.Model):
    """
        The Courier Table
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    tracking_url = models.CharField(max_length=250, default=None, blank=True, null=True)

    status_mapping = models.JSONField(default={}, null=True, blank=True)
    """
    JSON dictionary contain Status in the system and the statuses in the Courier page to unify the status and to be able to track

    example: 
 .. code-block:: json
        :linenos:

        {
            "Cancelled": "",
            "Delivered": "Delivered",
            "Failed": "",
            "New": "",
            "Pending": "Picked Up",
            "Rejected": "",
            "Shipped": "Out For Delivery",
            "Shipping": "In Transit"
        }

    """
    outer_script_path = models.CharField(max_length=250, default=None, null=True,
                                         help_text='In case of outer script needed')
    """
    Dotted path for the outer class for tracking, if the field is not empty then the script will run.
    example: main_app.api.trackers.Tracker
    .. note:: - the class will be called and package object will be passed as parameter
              - the script must update the package status
              - this method is not very secured so PLEASE use it with caution
    
    """
    is_active = models.BooleanField(default=True,help_text="The courier will not ba available if is_active=False")

    automatic_run = models.BooleanField(default=True,help_text="To run with celery every 12 hours")

    invalid_clause = models.CharField(max_length=100, null=True, blank=True)
    """
    Invalid clause in the Courier page to indicate that the tracking number is not valid or the data are not valid anymore
    """
    track_details_div = models.JSONField(default=dict)
    status_div = models.JSONField(default=dict)
    date_div = models.JSONField(default=dict)
    time_div = models.JSONField(default=dict)
    location_div = models.JSONField(default=dict)
    """
    fields track_details_div,status_div,date_time_div,location_div are JSON dictionaries contain basic search keys and values

    example 1 : The value in the span needed <div class=trk-wrap-content-right><span></span></div> so the dictionary will be like the following
 .. code-block:: json
        :linenos:

        {
            "attribute": "class", 
            "child": "span",
            "tag": "div",
            "value": "trk-wrap-content-right"
        }
    
    example 2 : The value in the heading needed and there are not attributes or children <h4></h4> so the dictionary will be like the following

 .. code-block:: json
        :linenos:

        {
            "tag": "h4"
        }
    """

    def __str__(self):
        return u'%s' % self.name

    class Meta:
        db_table = 'Courier'

class Package(models.Model):
    id = models.AutoField(primary_key=True)
    track_number = models.CharField(max_length=100, unique=True, null=False)
    courier = models.ForeignKey('Courier', on_delete=models.DO_NOTHING, default=None)
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, default=None)
    name = models.CharField(max_length=100)
    price = models.CharField(max_length=100,null=True,blank=True,default=0)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    status_log = models.JSONField(default={}, null=True, blank=True)
    status = models.ForeignKey(CStatus, default=1, on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def serialize(self):
        data = {
            'name': self.name,
            'source': self.source,
            'destination': self.destination,
            'date_created': self.date_created.isoformat()
        }
        return json.dumps(data)

    def __str__(self):
        return u'%s' % self.name

    class Meta:
        db_table = 'Package'
        ordering = ('-date_created',)
