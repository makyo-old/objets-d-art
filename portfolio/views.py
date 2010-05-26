from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from portfolio.models import *

def smart_list(request, type):
    objects = (Score,
               Recording,
               Writing,
               Image,
               Website,
               Program)[type].objects.filter(part_of_work__isnull = True)
    mps = MultiPart.objects.filter(media = str(type))
    return render_to_response('portfolio/%s_list.html' % MEDIA[type][1].lower(), context_instance = RequestContext(request, {'objects': objects, 'mps': mps}))

def with_tags(request, tag, type):
    tag = tag.replace('_', ' ')
    query = get_object_or_404(Tag, name = tag)
    objects = TaggedItem.objects.get_by_model((Score, Recording, Writing, Image, Website, Program)[type], query)
    return render_to_response('portfolio/%s_list_by_tag.html' % MEDIA[type][1].lower(), context_instance = RequestContext(request, {'objects': objects}))

def smart_show(request, slug, type):
    object = get_object_or_404((Score, Recording, Writing, Image, Website, Program, MultiPart)[type], slug = slug)
    if type == 6: # MultiPart
        if (request.method == 'GET') and (request.GET.get('asx', None) == 'true'):
            return render_to_response('portfolio/playlist.xml', context_instance = RequestContext(request, {'mp_object': object}))
        else:
            return render_to_response('portfolio/mp_%s_detail.html' % object.get_media_display().lower(), context_instance = RequestContext(request, {'mp_object': object}))
    else: 
        if (request.method == 'GET') and (request.GET.get('asx', None) == 'true'):
            return render_to_response('portfolio/playlist.xml', context_instance = RequestContext(request, {'mp_object': (object)}))
        else:
            return render_to_response('portfolio/%s_detail.html' % MEDIA[type][1].lower(), context_instance = RequestContext(request, {'object': object}))

def score_ajax(request, slug):
    return render_to_response('portfolio/score_ajax.html', context_instance = RequestContext(request, {'object': get_object_or_404(Score, slug = slug)}))

def recording_ajax(request, slug):
    return render_to_response('portfolio/recording_ajax.html', context_instance = RequestContext(request, {'object': get_object_or_404(Recording, slug = slug)}))

def mp_recording_ajax(request, slug):
    return render_to_response('portfolio/mp_recording_ajax.html', context_instance = RequestContext(request, {'object': get_object_or_404(MultiPart, slug = slug)}))
