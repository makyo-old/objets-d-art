from django.db import models
from django.contrib.auth.models import User
from store.checkout import get_controller
from tagging.fields import TagField

class Creator(models.Model):
    user = models.ForeignKey(User)
    profile = models.TextField()
    website = models.URLField(blank = True)

    def __unicode__(self):
        return self.user.get_full_name()

    def get_absolute_url(self):
        return "/store/creator/%s/" % self.user.username

class Product(models.Model):
    # Checkout stuff
    STATUS_CHOICES = (
            ('0', 'Live'),
            ('1', 'Coming Soon'),
            ('2', 'Out-of-Print'),
            ('3', 'Hidden')
            )

    sku = models.SlugField()
    status = models.CharField(max_length = 1, choices = STATUS_CHOICES)
    name = models.CharField(max_length = 250)
    short_desc = models.CharField(max_length = 500)
    width = models.DecimalField(max_digits = 3, decimal_places = 1)
    length = models.DecimalField(max_digits = 3, decimal_places = 1)
    height = models.DecimalField(max_digits = 3, decimal_places = 1)
    weight = models.DecimalField(max_digits = 3, decimal_places = 1)
    price = models.DecimalField(max_digits = 6, decimal_places = 2)

    # Product stuff
    DIFFICULTY_CHOICES = (
            ('1', 'Grade 1'),
            ('2', 'Grade 2'),
            ('3', 'Grade 3'),
            ('4', 'Grade 4'),
            ('5', 'Grade 5'),
            ('6', 'Grade 6'),
            ('7', 'Grade 7')
            )

    CATEGORY_CHOICES = (
            ('A', 'Concert'),
            ('B', 'Sacred'),
            ('C', 'Occasional'),
            ('D', 'Educational'),
            ('E', 'Jazz'),
            ('F', 'Pop/Rock'),
            ('G', 'Textbooks/Classroom Materials'),
            ('H', 'Other')
            )

    long_desc = models.TextField()
    creator = models.ForeignKey('Creator')
    pages = models.IntegerField()
    duration = models.DecimalField(max_digits = 4, decimal_places = 1)
    difficulty = models.CharField(max_length = 1, choices = DIFFICULTY_CHOICES)
    category = models.CharField(max_length = 1, choices = CATEGORY_CHOICES)
    ensemble = models.CharField(max_length = 120)
    instrumentation = models.CharField(max_length = 120)
    tags = TagField()

    def get_unique(self, field):
        # this is bad, but it works
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("select distinct " + field.split(' ')[0] + " from store_product")
        if cursor.rowcount == -1:
            return None
        else:
            rows = cursor.fetchall()
            for i in range(0,len(rows)):
                rows[i] = str(rows[i][0])
            return rows

    def get_duration_display(self):
        import math
        hours = 0
        minutes = 0
        seconds = 0
        if self.duration > 60:
            hours = int(math.floor(self.duration / 60))
        minutes = int(math.floor(self.duration))
        seconds = int(60 * (self.duration - minutes))
        return "%02d:%02d:%02d" % (hours, minutes, seconds)

    def __unicode__(self):
        return "MJS-MP#%(sku)s - %(name)s" % {'sku': self.sku, 'name': self.name}

    def get_absolute_url(self):
        return "/store/product/%s/" % self.sku

    class Meta:
        ordering = ['sku']

class Sample(models.Model):
    TYPE_CHOICES = (
            ('A', 'Audio sample'),
            ('D', 'Page sample'),
            ('V', 'Video sample'),
            ('E', 'External sample'),
            )
    product = models.ForeignKey('Product')
    type = models.CharField(max_length = 1, choices = TYPE_CHOICES)
    url = models.URLField()

    def __unicode__(self):
        return "%s - %s" % (self.product, self.get_type_display())

    def html(self):
        ext = self.url[len(self.url) - 3:]
        if ext == 'mp3':
            return '<embed src="http://media.mjs-publishing.com/mediaplayer.swf" width="470" height="20" allowscriptaccess="always" allowfullscreen="true" flashvars="height=20&width=470&file=%s" />' % self.url
        elif ext == 'pdf':
            return '<a target="_blank" href="%s"><img src="http://media.mjs-publishing.com/pdfData/pdficon_large.gif" alt="[PDF]" width="20" /> [View Document]</a><br />Requires Adobe Reader:<br /><a href="http://get.adobe.com/reader/"><img src="http://media.mjs-publishing.com/pdfData/get_adobe_reader.gif" alt="[get Adobe Reader]" /></a>' % self.url
        else:
            return '<a target="_blank" href="%s">External Sample</a>' % self.url

        class Meta:
            ordering = ['id']

class Item(models.Model):
    cart = models.ForeignKey('Cart')
    product = models.ForeignKey('Product')
    quantity = models.IntegerField()

class Cart(models.Model):
    STATUS_CHOICES = (
            ('0', 'Finished Shopping'),
            ('1', 'Still Shopping'),
            ('2', 'System Error'),
            ('3', 'User reported problem'),
            ('4', 'Offline Order'),
            )

    owner = models.ForeignKey(User)
    name = models.CharField(max_length = 125)
    is_active = models.OneToOneField(User, null = True, blank = True, related_name = 'active_cart')
    is_shared = models.BooleanField(default = False)
    ctime = models.DateTimeField(auto_now_add = True, blank = False)
    mtime = models.DateTimeField(auto_now = True, blank = False)
    local_status = models.CharField(max_length = 1, choices = STATUS_CHOICES)
    state = models.CharField(max_length = 16, blank = True)
    payment = models.CharField(max_length = 16, blank = True)
    google_id = models.CharField(max_length = 255, blank = True)
    cart_xml = models.TextField(blank = True)
    
    
    def get_cart(self):
        from gchecky.model import *
        controller = get_controller()

        return controller.prepare_order(
                order = checkout_shopping_cart_t(
                    shopping_cart = shopping_cart_t(
                        items = [
                            item_t(
                               name = item.product.name,
                               description = item.product.short_desc,
                               unit_price = price_t(
                                   value = float(item.product.price),
                                   currency = 'USD'
                                   ),
                               item_weight = item_weight_t(
                                   value = float(item.product.weight),
                                   unit = 'LB'
                                   ),
                               quantity = item.quantity,
                               merchant_item_id = item.product.sku
                               ) for item in self.item_set.all()
                            ],
                        merchant_private_data = self.id
                        ),
                    checkout_flow_support = checkout_flow_support_t(
                        #XXX
                        edit_cart_url = 'http://sandbox.mjs-publishing.com/store/cart/%s/?action=decheckout' % self.id,
                        continue_shopping_url = 'http://sandbox.mjs-publishing.com/store/',
                        #/XXX
                        #tax_tables = tax_tables_t(
                        #    merchant_calculated = False,
                        #    default = default_tax_table_t(
                        #        tax_rules = [
                        #            default_tax_rule_t(
                        #                shipping_taxed = True,
                        #                rate = 0.059,
                        #                tax_area = tax_area_t(
                        #                    us_zip_pattern = '805*'
                        #                    )
                        #                ),
                        #            default_tax_rule_t(
                        #                shipping_taxed = True,
                        #                rate = 0.029,
                        #                tax_area = tax_area_t(
                        #                    us_state = 'CO'
                        #                    )
                        #                )
                        #            ]
                        #        )
                        #    ),
                        shipping_methods = shipping_methods_t(
                            carrier_calculated_shippings = [
                                carrier_calculated_shipping_t(
                                    carrier_calculated_shipping_options = [
                                        carrier_calculated_shipping_option_t(
                                            price = price_t(
                                                value = (self.total_weight() * 2 + 3),
                                                currency = 'USD'
                                                ),
                                            shipping_company = 'USPS',
                                            carrier_pickup = 'DROP_OFF',
                                            shipping_type = 'Priority Mail'
                                            ),
                                        carrier_calculated_shipping_option_t(
                                            price = price_t(
                                                value = (self.total_weight() * 0.5 + 6.79),
                                                currency = 'USD'
                                                ),
                                            shipping_company = 'FedEx',
                                            carrier_pickup = 'DROP_OFF',
                                            shipping_type = 'Ground'
                                            )
                                        ],
                                    shipping_packages = [
                                        shipping_package_t(
                                            height = measure_t(
                                                value = self.get_height(),
                                                units = 'IN'
                                                ),
                                            length = measure_t(
                                                value = self.greatest_length(),
                                                units = 'IN'
                                                ),
                                            width = measure_t(
                                                value = self.greatest_width(),
                                                units = 'IN'
                                                ),
                                            ship_from = ship_from_t(
                                                id = 'FOCO',
                                                city = 'Fort Collins',
                                                region = 'CO',
                                                postal_code = '80425',
                                                country_code = 'US'
                                                )
                                            )
                                        ]
                                    )
                                ]
                            )
                        ),
                    ),
                    diagnose = False
                )

    def get_total(self):
        price = 0
        for item in self.item_set.all():
            price += item.product.price * item.quantity
        return price

    def get_height(self):
        height = 0
        for item in self.item_set.all():
            height += item.product.height * item.quantity
        return height

    def greatest_length(self):
        length = 0
        for item in self.item_set.all():
            if item.product.length > length:
                length = item.product.length
        return length

    def greatest_width(self):
        width = 0
        for item in self.item_set.all():
            if item.product.width > width:
                width = item.product.width
        return width

    def total_weight(self):
        weight = 0
        for item in self.item_set.all():
            weight += item.product.weight * item.quantity
        return float(weight)

    def __unicode__(self):
        return "%s's cart: %s" % (self.owner.username, self.name)

    @models.permalink
    def get_absolute_url(self):
        return ('store.views.cart_handler', [str(self.id)])

class Message(models.Model):
    cart = models.ForeignKey('Cart', blank = True, null = True)
    serial = models.CharField(max_length = 255, blank = True, null = True)
    tag = models.CharField(max_length = 16, default = '', blank = False)
    input_xml = models.TextField(blank = True, null = True)
    output_xml = models.TextField(blank = True, null = True)
    error = models.CharField(max_length = 255, blank = True, null = True)
    description = models.TextField(blank = True, null = True)
    ctime = models.DateTimeField(auto_now_add = True)
    mtime = models.DateTimeField(auto_now = True)

class Transaction(models.Model):
    TRANSACTION_TYPES = (
            ('S', 'Sale'),
            ('P', 'Payment'),
            ('C', 'Credit'),
            ('E', 'Expense'),
            ('A', 'Asset purchase'),
            )

    date = models.DateField(auto_now_add = True)
    type = models.CharField(max_length = 1, choices = TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits = 6, decimal_places = 2)
    cart = models.ForeignKey('Cart', blank = True, null = True)
    description = models.TextField(blank = True)

    def __unicode__(self):
        if self.amount < 0:
            return "($%s) - %s" % (str(self.amount), self.get_type_display())
        else:
            return "$%s - %s" % (str(self.amount), self.get_type_display())

def log_transaction(sender, **kwargs):
    i = kwargs['instance']
    if i.local_status == '0':
        from django.contrib.sites.models import Site
        if Transaction.objects.filter(cart = i).count() == 0 and Site.objects.get_current().domain == 'mjs-publishing.com':
            new_transaction = Transaction(
                    type = 'S',
                    amount = i.get_total(),
                    cart = i,
                    description = "")
            new_transaction.save()

models.signals.post_save.connect(log_transaction, sender = Cart)
