from django.contrib.sitemaps import Sitemap
from store.models import Product, Creator

class ProductSitemap(Sitemap):
    changefreq = "never"
    priority = 0.7

    def items(self):
        return Product.objects.exclude(status__exact = '3')

class CreatorSitemap(Sitemap):
    changefreq = "never"
    priority = 0.8

    def items(self):
        return Creator.objects.all()
