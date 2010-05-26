from django.http import HttpResponseServerError, HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list
from django.template import RequestContext
from store.models import *
from store.checkout import get_controller
from tagging.models import Tag, TaggedItem

def gc_callback(request, input_xml = None, safe_to_raise = False):
    controller = get_controller()
    if input_xml is None:
        if request.method != "POST":
            return HttpResponseServerError("Incorrect request method")
        input_xml = request.raw_post_data
    try:
        output_xml = controller.receive_xml(input_xml)
        return HttpResponse(output_xml, mimetype='text/xml')
    except Exception, exc:
        if safe_to_raise:
            raise
        return HttpResponseServerError(str(exc))

def creators(request):
    creator_list = Creator.objects.all()
    return render_to_response('store/creator_list.html', context_instance=RequestContext(request, {'creator_list': creator_list}))

def creator_detail(request, username = None):
    creator = get_object_or_404(Creator, user__username__exact = username)
    return render_to_response('store/creator_detail.html', context_instance=RequestContext(request, {'creator': creator}))

def product_detail(request, slug = None):
    product = get_object_or_404(Product, sku = slug)
    if product.status == '3':
        return HttpResponseServerError('Permission Denied')
    if request.method == 'POST':
        cart = None
        if request.user.cart_set.filter(local_status = '1').count():
            cart = request.user.active_cart
        else:
            cart = Cart(owner = request.user, name = "Default", is_active = request.user, is_shared = False, local_status = '1')
            cart.save()
            cart.name = "Cart ID:" + str(cart.id)
            cart.save()
            request.user.message_set.create(message = '<span class="success">Created new cart: %s</span>' % cart.name)
        if cart.item_set.filter(product__pk = product.id).count() == 0:
            newitem = Item(cart = cart, product = product, quantity = request.POST['quantity'])
            newitem.save()
            request.user.message_set.create(message = "<span class=\"success\">Item '%(item)s' successfully added to cart '%(cart)s'</span>" % {'item': product.name, 'cart': cart.name})
        else:
            olditem = cart.item_set.get(product__sku = slug)
            olditem.quantity += int(request.POST['quantity'])
            olditem.save()
            request.user.message_set.create(message = "<span class=\"success\">Item '%(item)s's quantity was successfully updated in cart '%(cart)s'</span>" % {'item': product.name, 'cart': cart.name})
        return HttpResponseRedirect("/store/cart/%d/" % cart.id)
    return render_to_response('store/product_detail.html', context_instance=RequestContext(request, {'product': product}))

def filter_products(request, filter = None, filter_by = None, page = 1):
    query = Product.objects.filter(**{str(filter_by): str(filter)}).exclude(status__exact = '3')
    if query.count() == 0:
        return render_to_response('store/no_products.html', context_instance=RequestContext(request))
    paginate = request.GET.get('paginate_by', None) or 25
    if len(filter) == 1:
        #XXX This is way ugly, but we gotta get the choice display somehow.
        if filter_by.split('__')[0] == 'difficulty':
            filter = query[0].get_difficulty_display()
        elif filter_by.split('__')[0] == 'category':
            filter = query[0].get_category_display()
    else:
        if filter_by.split('__')[0] == 'creator':
            filter = query[0].creator.user.get_full_name()
    return object_list(request, queryset = query, paginate_by = int(paginate), template_object_name = 'product', extra_context = {'filter_by': filter_by.split('__')[0], 'filter': filter, 'request': request, 'user': request.user, 'paginate_by': int(paginate)})

def with_tags(request, tag, object_id = None, page = 1):
    tag = tag.replace('_', ' ')
    query = get_object_or_404(Tag, name = tag)
    products = TaggedItem.objects.get_by_model(Product, query)
    paginate = request.GET.get('paginate_by', None) or 25
    return object_list(request, queryset = products, paginate_by = int(paginate), template_object_name = "product", extra_context = {'tag': tag, 'request': request, 'user': request.user})

def list_fields(request, field = None):
    rows = Product.objects.all()[0].get_unique(field)
    return render_to_response('store/list_fields.html', context_instance=RequestContext(request, {'rows': rows, 'field': field}))


@login_required
def cart_list(request):
    cart_list = request.user.cart_set.filter(local_status = '1')
    return render_to_response('store/cart_list.html', context_instance=RequestContext(request, {'cart_list': cart_list}))

@login_required
def create_cart(request):
    if request.user.cart_set.filter(local_status = '1').count() == 5:
        request.user.message_set.create(message = '<span class="error">You may only maintain 5 carts at a time!</span>')
        return HttpResponseRedirect('/store/carts/')
    if request.method == 'POST':
        cart = request.user.cart_set.create(
                owner = request.user,
                name = 'Default',
                is_shared = False,
                local_status = '1')
        if Cart.objects.filter(is_active = request.user).count() == 0:
            cart.is_active = request.user
        cart.is_shared = request.POST.get('shared', None) or False
        cart.save()
        cart.name = request.POST.get('newname', None) or "Cart ID:" + str(cart.id)
        cart.save(force_update = True)
        request.user.message_set.create(message = '<span class="success">New cart successfully created!</span>')
        return HttpResponseRedirect('/store/carts/')
    else:
        return render_to_response('store/cart_form.html', context_instance=RequestContext(request))

def cart_handler(request, object_id):
    cart = get_object_or_404(Cart, id = object_id)
    #TODO switch to a python 'switch' statement:
    #  return {'delete', _cart_delete(cart), ...}[$request.GET.get('action', 'list')]
    #see http://simonwillison.net/2004/May/7/switch/
    if request.GET and cart.owner == request.user:
        if request.GET['action'] == 'delete':
            if cart.local_status == '1':
                if request.GET.get('confirm', None) == 'yes':
                    cart.delete()
                    request.user.message_set.create(message = '<span class="warning">Cart successfully deleted!</span>')
                    return HttpResponseRedirect('/store/carts/')
                else:
                    return render_to_response('store/cart_confirm_delete.html', context_instance=RequestContext(request, {'cart': cart}))
            else:
                request.user.message_set.create(message = "<span class=\"error\">Unable to delete cart, as it is flagged as '%s'!</span>" % cart.get_local_status_display())
                return cart_list(request)
        elif request.GET['action'] == 'update' and request.method == 'POST':
            if cart.local_status == '1':
                for k in request.POST:
                    if (k == 'remove' or (k.startswith('q') and request.POST[k] == 0)):
                        item = Item.objects.get(id = int(request.POST[k]))
                        item.delete()
                        if cart.item_set.count() < 1:
                            cart.delete()
                            request.user.message_set.create(message = '<span class="warning">Cart emptied and deleted</span>')
                        else:
                            request.user.message_set.create(message = '<span class="warning">Item deleted</span>')
                    if k.startswith('q'):
                        item = Item.objects.get(id = int(k[1:]))
                        item.quantity = request.POST[k]
                        item.save()
                cart.save()
                request.user.message_set.create(message = '<span class=\"success\">Cart successfully updated</span>')
                return HttpResponseRedirect("/store/cart/%s/" % cart.id)
        elif request.GET['action'] == 'activate':
            if request.user.active_cart:
                oldcart = request.user.active_cart
                oldcart.is_active = None
                oldcart.save()
            cart.is_active = request.user
            request.user.message_set.create(message = '<span class="success">This is now your active cart</span>')
            cart.save()
        elif request.GET['action'] == 'rename':
            cart.name = request.POST['newname']
            request.user.message_set.create(message = '<span class="success">Cart successfully renamed</span>')
            cart.save()
            return HttpResponseRedirect("/store/cart/%s/" % cart.id)
        elif request.GET['action'] == 'share':
            cart.is_shared = True
            request.user.message_set.create(message = '<span class="success">This cart is now publicly viewable!  Feel free to share the URL.</span>')
            cart.save()
            return HttpResponseRedirect("/store/cart/%s/" % cart.id)
        elif request.GET['action'] == 'unshare':
            cart.is_shared = False
            cart.save()
            request.user.message_set.create(message = '<span class="success">This cart is now private, only you will be able to see it.</span>')
            return HttpResponseRedirect("/store/cart/%s/" % cart.id)
        elif request.GET['action'] == 'checkout':
            import urllib2
            import xml.dom.minidom
            from base64 import b64encode
            gc = cart.get_cart()
            req = urllib2.Request(url = settings.CHECKOUT_URL, data = gc.xml)
            req.add_header('Authorization', 'Basic %s' % b64encode(settings.CHECKOUT_VENDOR_ID + ':' + settings.CHECKOUT_MERCHANT_KEY))
            req.add_header('Content-Type', 'application/xml; charset=UTF-8')
            req.add_header('Accept', 'application/xml; charset=UTF-8')
            try:
                response = xml.dom.minidom.parseString(urllib2.urlopen(req).read())
                if not response.getElementsByTagName('redirect-url')[0].childNodes[0].data.startswith('https'):
                    return HttpResponseServerError(response + redirect_url)
                else:
                    cart.local_status = '0'
                    cart.is_active = None
                    cart.save()
                    redirect_url = response.getElementsByTagName('redirect-url')[0].childNodes[0].data.replace('&amp;', '&')
                    return HttpResponseRedirect(redirect_url)
            except urllib2.HTTPError, e:
                return HttpResponseServerError(e.fp.read())
        elif request.GET['action'] == 'decheckout':
            cart.local_status = '1'
            cart.save()
            transaction = Transaction.objects.filter(cart = cart)
            if transaction:
                transaction.delete()
    elif cart.is_shared == True and cart.owner != request.user:
        return render_to_response('store/cart_detail_limited.html', context_instance=RequestContext(request, {'cart': cart}))
    return render_to_response('store/cart_detail.html', context_instance=RequestContext(request, {'cart': cart})) 
