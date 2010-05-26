from django.conf.urls.defaults import *
from store.models import *

urlpatterns = patterns('store.views',
        (r'^googlecheckout/$', 'gc_callback'),

        (r'^product/(?P<slug>[a-z0-9_-]+)/$', 'product_detail'),

        (r'^products/difficulty/(?P<filter>[1-7])/$', 'filter_products', {'filter_by': 'difficulty__exact'}),
        (r'^products/category/(?P<filter>[A-G])/$', 'filter_products', {'filter_by': 'category__iexact'}),
        (r'^products/ensembles/$', 'list_fields', {'field': 'ensemble'}),
        (r'^products/ensemble/(?P<filter>.+)/$', 'filter_products', {'filter_by': 'ensemble__iexact'}),
        (r'^products/instrumentations/$', 'list_fields', {'field': 'instrumentation'}),
        (r'^products/instrumentation/(?P<filter>.+)/$', 'filter_products', {'filter_by': 'instrumentation__iexact'}),
        (r'^products/tag/(?P<tag>[-_a-zA-Z0-9]+)/$', 'with_tags'),
        (r'^products/creators/$', 'creators'),
        (r'^products/creator/(?P<filter>[-_a-zA-Z0-9]+)/$', 'filter_products', {'filter_by': 'creator__user__username__iexact'}),

        (r'^creator/(?P<username>[-_a-zA-Z0-9]+)/$', 'creator_detail'),

        (r'^carts/$', 'cart_list'),
        (r'^cart/(?P<object_id>\d+)/$', 'cart_handler'),
        (r'^cart/add/$', 'create_cart'),
        (r'^ledger/', include('store.ledger.urls')),
)
