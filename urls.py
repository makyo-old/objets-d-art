from django.conf.urls.defaults import *
from store.models import *
from sitemaps import *
from django.contrib.sitemaps import FlatPageSitemap
from django.contrib import admin
admin.autodiscover()

sitemaps = {
        'products': ProductSitemap,
        'creators': CreatorSitemap,
        }

urlpatterns = patterns('',
    (r'^$', 'blog.views.front'),
    (r'^crossdomain.xml$', 'django.views.generic.simple.direct_to_template', {'template': 'flatpages/crossdomainpolicy.xml'}),
    (r'^sitemap.xml$', 'django.views.generic.simple.direct_to_template', {'template': 'flatpages/sitemap.xml'}),
    (r'^sitemap-other.xml$', 'django.views.generic.simple.direct_to_template', {'template': 'flatpages/sitemap-other.xml'}),
    (r'^sitemap-store.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    (r'^sitemap-flatpages.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': { 'flatpages': FlatPageSitemap }}),
    (r'^store/$', 'blog.views.storefront'),
    (r'^~(?P<username>[-_a-zA-Z0-9]+)/$', 'store.views.creator_detail'),
    (r'^~(?P<filter>[-_a-zA-Z0-9]+)/products/$', 'store.views.filter_products', {'filter_by': 'creator__user__username__iexact'}),
    (r'^store/', include('store.urls')),
    (r'^portfolio/', include('portfolio.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^forums/', include('forum.urls')),

    (r'^accounts/view/(?P<username>[-_a-zA-Z0-9]+)/$', 'usermgmt.views.user_view'),
    (r'^accounts/interest/(?P<tag>[-_a-zA-Z0-9]+)/$', 'usermgmt.views.with_tags'),
    (r'^accounts/profile/$', 'usermgmt.views.user_home'),
    (r'^accounts/profile/edit/$', 'usermgmt.views.user_edit'),
    (r'^accounts/', include('registration.urls')),
    (r'^about/contact/$', 'usermgmt.views.contact')
)
        ##(r'^store/products/difficulties/$', 'difficulties') # FLATPAGE - template: store/about_flatpages.html
        ##(r'^store/products/categories/$', 'categories'), # FLATPAGE - template: store/about_flatpages.html
        ##(r'^store/products/tags/$', 'tag_cloud'), # FLATPAGE - template: store/tags.html
        ##(r'^account/interests/$', tag_cloud) # FLATPAGE - template: registration/tags.html
        #(r'^about/$') # FLATPAGE - template: flatpages/about.html
        #(r'^about/faq/$') # FLATPAGE - template: flatpages/about.html
        #(r'^about/submit/$') # FLATPAGE - template: flatpages/about.html
        #(r'^about/legal/$') # FLATPAGE - template: flatpages/about.html
        #(r'^about/ip/$') # FLATPAGE - template: flatpages/about.html
        #(r'^store/about/shipping/$') # FLATPAGE - template: flatpages/about.html
        #(r'^store/about/problems/$') # FLATPAGE - template: flatpages/about.html
