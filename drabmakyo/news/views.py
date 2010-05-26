from django.shortcuts import render_to_response
from django.template import RequestContext
from news.models import *

def cdp(request):
    return render_to_response('flatpages/crossdomainpolicy.xml')

def front(request):
    return _news(request, 'news/front.html')

def list(request):
    return _news(request, 'news/list.html')            

def _news(request, template):
    return render_to_response(template, context_instance = RequestContext(request, {'items': NewsItem.objects.all()}))
