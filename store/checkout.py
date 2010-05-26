from gchecky.controller import ControllerLevel_1, Controller
from gchecky import model as gmodel
from django.conf import settings

class GController(Controller):
    def __init__(self, automatically_charge = False, *args, **kwargs):
        self.automatically_charge = automatically_charge
        return super(GController, self).__init__(*args, **kwargs)

    def on_retrieve_order(self, order_id, context=None):
        from store.models import Cart
        if Cart.objects.filter(google_id = order_id).count() > 0:
            return Cart.objects.get(google_id = order_id)
        return None

    def handle_new_order(self, message, order_id, order, context):
        from store.models import Cart
        #XXX  set the Cart's cart_xml and google_id here, have to get that somehow
        cart = Cart.objects.get(pk = int(message.shopping_cart.merchant_private_data))
        cart.google_id = order_id,
        cart.cart_xml = message.toxml()
        cart.state = message.fulfillment_order_state
        cart.payment = message.financial_order_state
        cart.save()
        return gmodel.ok_t()

    def handle_order_state_change(self, message, order_id, order, context):
        assert order is not None
        if message.new_fulfillment_order_state != message.previous_fulfillment_order_state:
            order.state = message.new_fulfillment_order_state
        if message.new_financial_order_state != message.previous_financial_order_state:
            order.state = message.new_financial_order_state
        order.save

        if order.state == 'NEW' and order.payment == 'CHARGEABLE':
            self.charge_order(order_id, order.get_total())

        return gmodel.ok_t()

    def handle_charge_amount(self, message, order_id, order, context):
        assert order is not None
        if order.state == 'NEW':
            order.state = 'PROCESSING'
            order.local_status = '0'
            order.is_active = None
            self.process_order(order_id)
            order.save()
        return gmodel.ok_t()

    def handle_chargeback_amount(self, message, order_id, order, context):
        pass

    def on_xml_sent(self, context):
        self.__log(context = context, tag = 'to')

    def on_xml_received(self, context):
        self.__log(context = context, tag = 'from')

    def __log(self, context, tag, error = None, description = None):
        from store.models import Message
        cart = None
        if context.order_id is not None:
            cart = self.on_retrieve_order(order_id = context.order_id, context = context)
        else:
            context.serial = 'PLACEHOLDER' #XXX

        message = Message(cart = cart, serial = context.serial, tag = tag, input_xml = context.xml, output_xml = context.response_xml, error = error, description = description)
        message.save()

__controller__ = None
def get_controller():
    from store.checkout import __controller__
    if __controller__ is None:
        #__controller__ = ControllerLevel_1(
        __controller__ = GController(
                vendor_id = settings.CHECKOUT_VENDOR_ID,
                merchant_key = settings.CHECKOUT_MERCHANT_KEY,
                currency = settings.CHECKOUT_CURRENCY,
                is_sandbox = settings.CHECKOUT_IS_SANDBOX,#)
                automatically_charge = False)
    return __controller__
