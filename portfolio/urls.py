from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('portfolio.views',
    # Portfolio listing
    (r'^scores/$', 'smart_list', {'type': 0}),
    (r'^scores/tag/(?P<tag>[ -_a-zA-Z0-9]+)/$', 'with_tags', {'type': 0}),
    (r'^recordings/$', 'smart_list', {'type': 1}),
    (r'^recordings/tag/(?P<tag>[ -_a-zA-Z0-9]+)/$', 'with_tags', {'type': 1}),
    (r'^writing/$', 'smart_list', {'type': 2}),
    (r'^writing/tag/(?P<tag>[ -_a-zA-Z0-9]+)/$', 'with_tags', {'type': 2}),
    (r'^graphics/$', 'smart_list', {'type': 3}),
    (r'^graphics/tag/(?P<tag>[ -_a-zA-Z0-9]+)/$', 'with_tags', {'type': 3}),
    (r'^webdesign/$', 'smart_list', {'type': 4}),
    (r'^webdesign/tag/(?P<tag>[ -_a-zA-Z0-9]+)/$', 'with_tags', {'type': 4}),
    (r'^programming/$', 'smart_list', {'type': 5}),
    (r'^programming/tag/(?P<tag>[ -_a-zA-Z0-9]+)/$', 'with_tags', {'type': 5}),
    (r'^mixed/$', 'smart_list', {'type': 6}),

    # Portfolio viewing
    (r'^(work|book|gallery|websites|package|collection)/(?P<slug>[a-zA-Z0-9_-]+)/$', 'smart_show', {'type': 6}),
    (r'^score/(?P<slug>[a-zA-Z0-9_-]+)/$', 'smart_show', {'type': 0}),
    (r'^ajax/score/(?P<slug>[a-zA-Z0-9_-]+)/$', 'score_ajax'),
    (r'^recording/(?P<slug>[a-zA-Z0-9_-]+)/$', 'smart_show', {'type': 1}),
    (r'^ajax/recording/(?P<slug>[a-zA-Z0-9_-]+)/$', 'recording_ajax'),
    (r'^ajax/collection/(?P<slug>[a-zA-Z0-9_-]+)/$', 'mp_recording_ajax'),
    (r'^(story|chapter|article|letter)/(?P<slug>[a-zA-Z0-9_-]+)/$', 'smart_show', {'type': 2}),
    (r'^(photo|graphic)/(?P<slug>[a-zA-Z0-9_-]+)/$', 'smart_show', {'type': 3}),
    (r'^website/(?P<slug>[a-zA-Z0-9_-]+)/$', 'smart_show', {'type': 4}),
    (r'^program/(?P<slug>[a-zA-Z0-9_-]+)/$', 'smart_show', {'type': 5}),
)
