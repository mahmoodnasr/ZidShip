from django.http import Http404
from rest_framework import permissions
from rest_framework import serializers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from main_app.models import CStatus


class CStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CStatus
        fields = '__all__'


class CStatusViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = CStatus.objects.all()
    serializer_class = CStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
