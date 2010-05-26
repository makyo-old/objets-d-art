from django.conf.urls.defaults import *

urlpatterns = patterns('store.ledger.views',
        (r'^$', 'front'),
        (r'^creators/$', 'creators'),
        (r'^creator/(?P<filter>[-_a-zA-Z0-9]+)/$', 'filter_ledger', {'filter_by': 'cart__item_set__product__creator__user__username__exact', 'type': 'creator'}),
        (r'^products/$', 'products'),
        (r'^product/(?P<filter>[-_a-zA-Z0-9]+)/$', 'filter_ledger', {'filter_by': 'cart__item_set__product__sku__exact', 'type': 'product'}),
        (r'^business/$', 'filter_ledger', {}), # should return whole set
)

#query string
#  startdate=yyyy-mm-dd
#  duration=(day|week|month*|quarter|year|all)
#  format=(html*|latex|csv)
#  depth=(summary*|clean|full)
#    summary=number of transactions, amount earned/lost, etc
#    clean=summary plus individual transactions with no specific details
#    full=summary plus individual transactions with details
