from django.db.models import Count, Sum
from django.template.loader import render_to_string

from .models import Package, CStatus


def charts(request):
    import operator
    context = {}
    data = {item['status__description']: item['count'] for item in
            Package.objects.all().values('status__description').annotate(count=Count('status__description')).order_by()}
    labels = list(CStatus.objects.all().values_list('description', flat=True).order_by('description'))
    for item in labels:
        if item not in data.keys():
            data[item] = 0
    sorted_dict = {k: data[k] for k in sorted(data)}
    context['data'] = sorted_dict
    context['values'] = [v for k,v in sorted_dict.items()]
    context['labels'] = labels
    template = render_to_string("chart.html", context)
    return {"Charts": template}
